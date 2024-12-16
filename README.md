# ScreamFortressChecker
After so many [Scream Fortresses](https://wiki.teamfortress.com/wiki/Halloween_event), have you ever wondered if you
got all the items that can drop from the [Halloween Packages](https://wiki.teamfortress.com/wiki/Halloween_Package)? Then, this is for you!

With this tool you can check how many items you are missing and how many you have repeated.
Additionally, you can also choose to ignore items that are tradable (i.e. not
dropped from the halloween packages) or items with special qualities (strange, haunted, etc.).

## Screenshots 
Example of "Get Missing Items" feature:
![Example of 'Get Missing Items'](./readme_images/img1.jpg?raw=true "Title")
Example of "Get Repeated Items" feature:
![Example of 'Get Repeated Items'](./readme_images/img2.jpg?raw=true "Title")

## Installation 
This is mostly geared towards linux, but windows should provide a similar experience, given the pre-requisites.

 - Clone or download the repo through your preferred method. For instance, you could do:
```
git clone https://github.com/omediodomonte38/ScreamFortressChecker.git
```

- Move to the folder with 
```
cd ScreamFortressChecker
```

### Running locally

If you wish to run locally, you can use ```uv``` to install the dependencies from the ```pyproject.toml```.
In case you do not have ```uv``` installed you can run
```
pip3 install uv
```
and then create a venv and install the requirements with

```
uv venv
uv pip install --requirements pyproject.toml
```
Finally, run the app with

```
python3 src/app.py
```
This will serve the app on ```http://127.0.0.1:5000```, connecting with a browser will lead you the interface.

### Running with Docker

If you have Docker installed, you can intead, build and run it inside a container.
Build using
```
make build
```
and run the app with

```
make serve
```
This will serve the app on ```http://127.0.0.1:5000```, connecting with a browser will lead you the interface.

## Usage
To use the program you require your own [Steam API key](https://steamcommunity.com/dev?l=spanish), which can be easily obtained [here](https://steamcommunity.com/dev/apikey)

Additionally, you will need a link to a Steam profile whose inventory is public.

The "Get Missing Items!" button will, by default, get the items missing in your inventory, 
that can be dropped from halloween packages. By marking "Ignore Tradable" the tradable versions 
of items droppable by halloween packages are ignored, meaning they are not counted as present. Likewise, by marking "Ignore Qualities" 
items with special qualities such as Strange or Haunted will be ignored, not counting them as present. This could be
useful if you want all unique copies of the items.

The "Get Repeated Items!" button will, by default, get the items repeated in your inventory (i.e. multiple copies), 
that can be dropped from halloween packages. As previously, by marking "Ignore Tradable" the tradable versions 
of items droppable by halloween packages are not counted towards the total of repeated items. Finally, 
items with special qualities such as Strange or Haunted, not counting those as present. 

