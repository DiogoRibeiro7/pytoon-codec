# Notebook Examples

Follow these steps to work with the interactive notebook examples.

## 1. Install dependencies

```bash
poetry install
```

## 2. Activate a Poetry shell (or venv)

```bash
poetry shell
```

> Alternatively, you can use `poetry run` in each command without activating the shell.

## 3. Launch Jupyter

```bash
poetry run jupyter lab
```

Open the `examples/notebooks/pytoon_codec_intro.ipynb` notebook inside Jupyter Lab (or VS Code's notebook UI) and execute the cells in order.

## VS Code tip

If you prefer VS Code, use the Poetry environment as the interpreter (`Python: Select Interpreter`) and open the notebook file directly. VS Code will reuse the Poetry kernel automatically once selected.
