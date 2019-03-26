import click


@click.group()
def cli():
    pass


@click.command()
def init():
    click.echo('Initializes and loads data into GraphDB')


@click.command()
def reload():
    click.echo('Reloads the ontology cache')


cli.add_command(init)
cli.add_command(reload)
