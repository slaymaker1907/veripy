from collections.abc import Sequence, Mapping

def getgen(ob, name):
    if isinstance(ob, Mapping):
        return ob.get(name, None)
    elif isinstance(ob, Sequence) and isinstance(name, int):
        try:
            return ob[name]
        except IndexError:
            return None
    else:
        return getattr(ob, name, None)

class VerifierMonad:
    def __init__(self):
        self.constraints = []

    def add(self, pred, mess):
        def result(obj):
            if not pred(obj):
                return mess
        return None
        self.constraints.append(result)
        return self

    def _get_message(self, name, err):
        return 'Error with attribute: {0}. {1}'.format(name, err)

    def compose(self, name, other):
        self.constraints.append(self._comp_func(name, other))
        return self

    def _comp_func(self, name, other):
        def result(obj):
            temp = other(getgen(obj, name))
            if temp is not None:
                return self._get_message(name, temp)
            else:
                return None
        return result

    def compose_opt(self, name, other):
        base_con = self._comp_func(name, other)
        def soft_check(obj):
            if obj is not None:
                return base_con(obj)
            else:
                return None
        self.constraints.append(soft_check)
        return self

    def add_none(self, name):
        self.compose(name, VerifierMonad())
        return self

    def add_raw(self, con):
        self.constraints.append(con)
        return self

    def clone(self):
        result = VerifierMonad()
        result.constraints = list(self.constraints)

    def __call__(self, obj):
        if obj is None:
            return 'Object may not be null.'
        for constr in self.constraints:
            temp = constr(obj)
            if temp is not None:
                return temp
        return None
