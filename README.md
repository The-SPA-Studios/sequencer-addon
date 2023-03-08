# SPA Sequencer Addon

This add-on contains a set of tools that improve the sequence workflow in Blender.
It can be used for Storyboarding or Layout, to work simultaneously on different shots,
leveraging Blender's native concepts of _scenes_ and _cameras_, as well as the _Video Sequence Editor_ (VSE).

Features:
- Synchronised VSE and scene timelines.
- VSE based shot management system (add, rename, delete, etc.).
- Batch rendering shots from the VSE.
- Editorial import/export capabilities (based on OTIO).
- Shared folders (collection linking between scenes).

Note: Without the use of the [Blender SPA](https://github.com/The-SPA-Studios/blender) version, the following features will not work properly:
 - Timeline syncronization of scenes in the same window.
 - Batch rendering using the viewport render.

The add-on is shared as is, for the community to test, discuss, and hopefully draw inspiration for future Blender versions and tools.
The SPA Studios should not be expected to provide active support for any of the presented features.

## Install

To try out the full Blender SPA experience (including this add-on), download the portable build from [this link (Windows 64bits)](https://thespastudios.com/public-links/blender_spa-2.4.1-bundle-windows64.zip), unzip it and run Blender from there.

To test this add-on separately, download the latest release and install as any Blender add-on (see [documentation](https://docs.blender.org/manual/en/latest/editors/preferences/addons.html#installing-add-ons)).
Please note that some features will not work properly when used with an official Blender build.

## User Guide

User documentation is available [here](https://the-spa-studios.github.io/blender-spa-userdoc/).

## Demo

The sequencer workflow was presented at the 2022 Blender Conference:
https://youtu.be/0HNmJebYY8M?t=1937

## Contribute

Read more about the developer's setup in [CONTRIBUTING.md](./CONTRIBUTING.md).

## License

_SPA Sequencer Addon_ is licensed under the GNU General Public License, Version 3 or later.

A full copy of the GPLv3 license can be found at [COPYING.md](./COPYING.md).

### Additional Terms

As per section 7 of the GPLv3, the license is supplemented with the following additionnal term(s):

- Neither the name of the copyright holder nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.

## Authors

The SPA Studios pipeline team (2021-2023):
Antoine Boellinger ([@aboellinger](https://github.com/aboellinger)), Bryan Fordney ([@bryab](https://github.com/bryab)), Falk David ([@falkdavid](https://github.com/falkdavid)), Mickael Villain ([@micka-06](https://github.com/micka-06)), Nick Alberelli ([@NickTiny](https://github.com/NickTiny)), Paolo Fazio ([@PaoloFazio](https://github.com/PaoloFazio)), Yann Lanthony ([@yann-lty](https://github.com/yann-lty)).
