# sshcontroller
A simple script to monitor SSH access.

For every ssh (successful) access the script communicates the access result by email.

# configuration

Enter the email account information in the configuration file
```
config.ini
```

Open the sshcontroller.py file with a text editor and add the path to the
configuration file in the variable:

```
path_config
```

Make the script executable with the following command:

```
chmod +x sshcontroller.py
```

To add the script to the crontab type:

```
sudo crontab -e
```

and add the following command at the bottom of the page.

```
@reboot /usr/bin/python3 [path sshcontroller.py]
```
