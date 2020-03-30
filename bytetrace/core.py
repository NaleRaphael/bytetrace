import dis, builtins, sys
from pdb import Pdb as BuiltinPdb
from pdb import set_trace as _Pdb_set_trace


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


class Pdb(BuiltinPdb):
    def trace_dispatch(self, frame, event, arg):
        if self.quitting:
            return # None
        if event == 'opcode':
            return self.dispatch_opcode(frame, arg)
        if event == 'line':
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
        print('--- f_locals: {}'.format(frame.f_locals))
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


def set_trace(*, header=None, trace_opcode=True):
    pdb = Pdb()
    if header is not None:
        pdb.message(header)
    f = sys._getframe().f_back
    f.f_trace_opcodes = trace_opcode
    pdb.set_trace(f)
