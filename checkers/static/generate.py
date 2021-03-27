import os

import jinja2

from .src.vars_en import en_vars
from .src.vars_pt import pt_vars


def main():
    templates = ['index.html']
    languages = [('en', en_vars), ('pt', pt_vars)]
    dirname = os.path.dirname(__file__)

    env = jinja2.Environment(
        loader=jinja2.FileSystemLoader(os.path.join(dirname, 'src'))
    )

    for filename in templates:
        tmpl = env.get_template(filename + '.j2')
        for lc, lvars in languages:
            with open(os.path.join(dirname, lc, filename), 'w') as fp:
                fp.write(tmpl.render(lvars))


if __name__ == '__main__':
    main()
