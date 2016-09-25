from collections.abc import Sequence, Mapping, Callable, Iterable

class VerificationException(Exception):
    def __init__(self, bad_ob, *args, **vargs):
        super().__init__(*args, **vargs)
        self.bad_ob = bad_ob

def getgen(ob, name):
    if isinstance(ob, Mapping):
        result = ob.get(name, None)
    elif isinstance(ob, Sequence) and isinstance(name, int):
        try:
            result = ob[name]
        except IndexError:
            result = None
    else:
        result = getattr(ob, name, None)
    if result is not None and isinstance(result, Callable):
        return result()
    else:
        return result

class VerifierMonad:
    def __init__(self):
        self.constraints = []

    def add(self, pred, mess):
        def result(obj):
            if not pred(obj):
                return mess
        self.constraints.append(result)
        return self

    def _get_message(self, name, err):
        return 'Error with attribute: {0}. {1}'.format(name, err)

    def compose(self, name, other):
        self.constraints.append(self._comp_func(name, other))
        return self

    def _comp_func(self, name, other):
        assert other != None
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
        return result

    def to_iter(self):
        def make_iter(con):
            def result(lst):
                for item in lst:
                    temp = con(item)
                    if temp is not None:
                        return temp
                return None
            return result
        def check_type(ob):
            if not isinstance(ob, Iterable):
                return 'Object must be iterable.'
            else:
                return None
        constraints = [check_type] + [make_iter(con) for con in self.constraints]
        result = VerifierMonad()
        result.constraints = constraints
        return result

    def __call__(self, obj):
        if obj is None:
            return 'Object may not be null.'
        for constr in self.constraints:
            temp = constr(obj)
            if temp is not None:
                return temp
        return None

    def check(self, ob):
        result = self(ob)
        if result is not None:
            raise VerificationException(ob, result)

    def add_eq(self, attr_name, value):
        def constr(ob):
            if ob != value:
                return 'Expected value {0} but was {1}'.format(value, ob)
            else:
                return None
        result = VerifierMonad().add_raw(constr)
        return self.compose(attr_name, result)

    def add_neq(self, attr_name, value):
        def constr(ob):
            if ob == value:
                return 'Value should not be equal to {0} but was equal.'.format(value)
            else:
                return None
        result = VerifierMonad().add_raw(constr)
        return self.compose(attr_name, result)
