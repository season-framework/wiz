import season
import re

Annotation = season.util.std.stdClass()
Annotation.definition = wiz.model("workspace/build/annotation/definition")
Annotation.injection = wiz.model("workspace/build/annotation/injection")

Model = Annotation