import pandas as pd
import click

@click.group()
@click.option('--file', type=click.Path(exists=True))
@click.option('--filter-NaT', type=str, default=None)
@click.pass_context
def cli(ctx, file, filter_nat):
    df = pd.read_excel(file, skiprows=5)
    if filter_nat:
        df = df[df[filter_nat].isnull()]
    
    df = df[df.apply(lambda x: '-' not in x['Názov obce'], axis=1)]
    df = df[df['PSČ'].notnull()]
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
    ctx.obj['df'][list(cols)].to_csv(out_file)

if __name__ == "__main__":
    cli(obj={})
