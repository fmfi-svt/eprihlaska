import pandas as pd
import click
import re

top_regex = re.compile(r'^.. - ')


def obec_formatter(row):
    return top_regex.sub('', row['Okres'])


@click.group()
@click.option('--file', type=click.Path(exists=True))
@click.option('--filter-NaT', type=str, default=None)
@click.option('--sheet', type=str, default=0)
@click.pass_context
def cli(ctx, file, filter_nat, sheet):
    df = pd.read_excel(file, skiprows=3, sheet_name=sheet)
    if filter_nat:
        df = df[df[filter_nat].isnull()]
        df = df[df['id'] >= 0]

    df = df[df.apply(lambda x: '-' not in x['Názov obce'], axis=1)]
    df = df[df['PSČ'].notnull()]

    df['Okres'] = df.apply(obec_formatter, axis=1)

    ctx.obj['df'] = df


@cli.command()
@click.pass_context
def show(ctx):
    print(ctx.obj['df'].head(n=40))


@cli.command()
@click.option('--out-file', type=click.Path())
@click.argument('cols', nargs=-1)
@click.pass_context
def convert(ctx, out_file, cols):
    ctx.obj['df'][list(cols)].to_csv(out_file, index=False)


if __name__ == "__main__":
    cli(obj={})
