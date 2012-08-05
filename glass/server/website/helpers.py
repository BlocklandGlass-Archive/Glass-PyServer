from flask import Blueprint


class NestableBlueprint(Blueprint):
    def __init__(self, *args, **kwargs):
        Blueprint.__init__(self, *args, **kwargs)
        self.children = []

    def register_blueprint(self, blueprint, *args, **kwargs):
        self.children.append((blueprint, args, kwargs))

    def register(self, app, args, first_registration):
        for blueprint, bargs, bkwargs in self.children:
            bkwargs = bkwargs.copy()  # Clone bkwargs to make any changes non-permanent

            if "url_prefix" in bkwargs and "url_prefix" in args:
                bkwargs["url_prefix"] = args["url_prefix"] + bkwargs["url_prefix"]

            print args, self.url_prefix, bkwargs

            app.register_blueprint(blueprint, *bargs, **bkwargs)
        return Blueprint.register(self, app, args, first_registration)
