import dis, builtins, sys, inspect
from pdb import Pdb as BuiltinPdb


# build a map for opcodes that defined in `dis.hasconst`, `dis.hasfree`, ...
SPECIAL_COLLECTION = {v: getattr(dis, v) for v in dir(dis) if v[:3] == 'has'}
SPECIAL_OPCODE = {}
for name, values in SPECIAL_COLLECTION.items():
    SPECIAL_OPCODE.update({v: name for v in values})

COLLECTION_PROCESS = {
    'hasconst': lambda f, code, int_arg: code.co_consts[int_arg],
    'hasfree': lambda f, code, int_arg: (code.co_cellvars[int_arg]
        if int_arg < len(code.co_cellvars) else
        code.co_freevars[int_arg - len(code.co_cellvars)]),
    'hasname': lambda f, code, int_arg: code.co_names[int_arg],
    'haslocal': lambda f, code, int_arg: code.co_varnames[int_arg],
    'hasjrel': lambda f, code, int_arg: f.f_lasti + int_arg,
}


def set_traceop_flag(frame, enabled):
    while frame:
        frame.f_trace_opcodes = enabled
        frame = frame.f_back


class OPTracer(BuiltinPdb):
    def __init__(self, *args, **kwargs):
        super(OPTracer, self).__init__(*args, **kwargs)
        self.prompt = '(OPTracer) '

    def trace_dispatch(self, frame, event, arg):
        if self.quitting:
            return # None
        if event == 'opcode':
            return self.dispatch_opcode(frame, arg)
        if event == 'line':
            # skip `line` event if we are tracing opcode
            if frame.f_trace_opcodes:
                return self.trace_dispatch
            else:
                return self.dispatch_line(frame)
        if event == 'call':
            return self.dispatch_call(frame, arg)
        if event == 'return':
            return self.dispatch_return(frame, arg)
        if event == 'exception':
            return self.dispatch_exception(frame, arg)
        if event == 'c_call':
            return self.trace_dispatch
        if event == 'c_exception':
            return self.trace_dispatch
        if event == 'c_return':
            return self.trace_dispatch
        print('bdb.Bdb.dispatch: unknown debugging event:', repr(event))
        return self.trace_dispatch

    def dispatch_opcode(self, frame, arg):  # `arg` is always None here
        opcode, oparg = self.parse_opcode_oparg(frame)
        print('--- opcode: {}, oparg: {}'.format(dis.opname[opcode], oparg))
        self.user_line(frame)
        return self.trace_dispatch

    def parse_opcode_oparg(self, frame):
        f = frame
        code = f.f_code
        opcode, int_arg = code.co_code[f.f_lasti:f.f_lasti+2]
        oparg = None
        if opcode >= dis.HAVE_ARGUMENT:
            collection_type = SPECIAL_OPCODE.get(opcode, None)
            if collection_type and collection_type in COLLECTION_PROCESS:
                oparg = COLLECTION_PROCESS[collection_type](f, code, int_arg)
            else:
                oparg = int_arg
        return opcode, oparg

    def do_quit(self, arg):
        """q(uit)\nexit
        Quit from this opcode tracer. Entering this command again to quit
        from debugger (pdb).
        """
        if not self.botframe.f_trace_opcodes:
            return super(OPTracer, self).do_quit(arg)
        f = sys._getframe().f_back
        set_traceop_flag(f, False)
        self.prompt = '(pdb) '
        print('--- leaving opcode tracing mode ---')

    do_q = do_quit
    do_exit = do_quit

    def do_print_f_locals(self, arg):
        """print_f_locals expression
        Print `f_locals` of current frame.
        """
        print(self.curframe.f_locals)

    do_pfl = do_print_f_locals

    def do_trace_op(self, arg):
        """trace_op expression
        Enter mode for tracing opcode.
        """
        f = sys._getframe().f_back
        set_traceop_flag(f, True)
        self.prompt = '(OPTracer) '


def set_trace(*, header=None, trace_opcode=True):
    tracer = OPTracer()
    if header is not None:
        tracer.message(header)
    f = sys._getframe().f_back
    set_traceop_flag(f, True)
    tracer.set_trace(f)
