This is a simple client for connecting to the remote serial console of
an OpenStack Nova server, using the API implemented in the Juno release of
OpenStack.  You can read more about that support here:

- http://blog.oddbit.com/2014/12/22/accessing-the-serial-console-of-your-nova-servers/

## Usage

With valid OpenStack credentials available in your environment, you
can run `novaconsole` with the name or UUID of a Nova server:

    $ novaconsole my-server
    WARNING:novaconsole.client:connected to: ws://127.0.0.1:6083/?token=bdcea854-2566-4f3b-86ef-4791aba42eea
    WARNING:novaconsole.client:type "~." to disconnect

You can also provide a websocket URL directly on the command line:

    $ novaconsole --url ws://127.0.0.1:6083/?token=bdcea854-2566-4f3b-86ef-4791aba42eea
    WARNING:novaconsole.client:connected to: ws://127.0.0.1:6083/?token=bdcea854-2566-4f3b-86ef-4791aba42eea
    WARNING:novaconsole.client:type "~." to disconnect

In either case, you will have an interactive connection to the serial
console of your Nova server.  You can type `~.` to disconnect.  If you
find that the `~` conflicts with something (for example, `~` is also
used as the default escape character by `ssh`), you can specify a new
escape character with `-e`:

    $ novaconsole -e@ my-server
    WARNING:novaconsole.client:connected to: ws://127.0.0.1:6083/?token=3fd11349-cd64-4dac-bbe0-68c49e9e1dc9
    WARNING:novaconsole.client:type "@." to disconnect

## Server configuration

For this to work, your server must be configured to support serial
console access.  This is a typical default for most "cloud" specific
images, which will include something like `console=tty0
console=ttyS0,11500n81` on the kernel command line.  This provides
console output on both the graphical (vnc) console and the serial
console, and takes input from the serial console.

## Installation

You can install the package with `pip`:

    pip install git+http://github.com/larsks/novaconsole.git

Or you can clone the repository by hand and run `setup.py`:

    git clone http://github.com/larsks/novaconsole.git
    cd novaconsole
    python setup.py install

