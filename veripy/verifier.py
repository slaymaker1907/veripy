class VerifierMonad:
    def __init__(self):
        self.constraints = []

    def add(self, pred, mess):
        def result(obj):
            if not pred(obj):
                return mess
        return None
        self.constraints.append(result)

    def _get_message(self, name, err):
        return 'Error with attribute: {0}. {1}'.format(name, err)

    def compose(self, name, other):
        self.constraints.append(self._comp_func(name, other))

    def _comp_func(self, name, other):
        def result(obj):
            temp = other(obj)
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

    def add_none(self, name):
        self.compose(name, VerifierMonad())

    def __call__(self, obj):
        if obj is None:
            return 'Object may not be null.'
        for constr in self.constraints:
            temp = constr(obj)
            if temp is not None:
                return temp
        return None
