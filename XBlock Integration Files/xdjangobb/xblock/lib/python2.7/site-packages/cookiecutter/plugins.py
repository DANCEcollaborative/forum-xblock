import functools


def get_plugin_list():
    """
    1. look in repo_root/cookiecutter_plugins.py
    2. look in ~/.cookiecutter_plugins.py

    Audrey:
    1. For plugins you list repo_urls in a plugins.txt file (or other config file)
    """
    # Go to the place where we downloaded the repo root
    with work_in("repo_root"):
        # import the cookiecutter_plugins module
        import cookiecutter_plugins

        # plugins are any callable possessing a 'cookiecutter_function attribute'
        plugin_list = [x for x in cookiecutter_plugins.locals() if \
            callable(x) and \
            hasattr(x, "cookiecutter_function")]
    return plugin_list


def plugins_filter(plugins, function_name):
    """ Usage inside of generate_context:

            from plugins import plugins_filter
            for plugin in plugins_filter(plugins, "cookies"):
                context = plugin(context)

    """
    return [x for x in plugins if x.cookiecutter_function == function_name]






def secret_key(context):
    """ TODO: Try to improve this AWESOME password generator """
    context['cookiecutter']['secret_key'] = "password"
    return context

secret_key.cookiecutter_function = "context_post_prompt"








def datetime_object(context):
    """ Passes the datetime object into the context
            for now acts as a something to fail the filter
    """
    from datetime import datetime
    context['datetime'] = datetime
    return context
