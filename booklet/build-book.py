"""Build a reviewed trip composition, then produce shared verified imposition."""
import importlib.util
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / 'scripts'))
from context import load_context, slug_argument
import layout
from imposition import compose


def main():
    root, temporary, output, plan, trip = load_context(slug_argument())
    layout.configure(root, output, temporary, trip, plan['fonts'])
    sys.path.insert(0, str(root))
    spec = importlib.util.spec_from_file_location('trip_renderer', root / 'render.py')
    recipe = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(recipe)
    qa = recipe.render(plan)
    qa['imposition'] = compose(output / plan['outputs']['reading'], output / plan['outputs']['facing'],
                              output / plan['outputs']['printing'], plan['title'])
    (temporary / 'book-qa.json').write_text(json.dumps(qa, ensure_ascii=False, indent=2), encoding='utf8')
    print(f'Created {plan["pageCount"]} reading pages, facing preview and A4 print PDF in {output}')


if __name__ == '__main__':
    main()
