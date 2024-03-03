def build(*args):
    if len(args) < 1:
        print("wiz command workspace build [projectName]")
        return

    project = args[0]
    wiz.project.checkout(project)
    builder = wiz.ide.plugin.model("builder")
    builder.build()
