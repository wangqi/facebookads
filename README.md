# Facebook Advertisement Tools

This is a set of tools that help you manage Facebook advertisements

## Command Line Tools

### fb_monitor_cost.py

It is used to monitor the Facebook spending and send notification to given receivers

```
usage: fb_monitor_cost.py [-h] [-c CONFIG] (-m | -a) [-t THRESHOLD]

Facebook Spending Monitor

optional arguments:
  -h, --help            show this help message and exit
  -c CONFIG, --config CONFIG
                        The absoluate path to configuration file.
  -m, --monitor         Monitor facebook spending and send message to
                        reveicers
  -a, --alarm           Monitor facebook spending and notify receivers only
                        when the spending is above the threshold
  -t THRESHOLD, --threshold THRESHOLD
                        Specify the threshold that 'alarm' mode will check.
```

You can also setup a crontab to monitor the facebook spending.

```
# crontab rule: check facebook spending every hour
0 * * * * python3 /path/to/fb_monitor_cost.py -c /path/to/facebookads.cfg -m
```

### fb_targetspec.py

It is used to export the facebook targeting spec and query the esstimate advertisement costs.
It can output tab-separated file.

```
usage: fb_targetspec.py [-h] [-c CONFIG] {query,import} ...

Facebook Targetting Spec Tool

positional arguments:
  {query,import}        Supported commands
    query               Query and output the specified countries' spec and
                        reach estimate data.
    import              Import the targeting_spec generated by 'query' command
                        and created audience groups

optional arguments:
  -h, --help            show this help message and exit
  -c CONFIG, --config CONFIG
                        The absoluate path to configuration file.
```

It supports two commands: ```query``` and ```import```

For the query command:

```
usage: fb_targetspec.py query [-h] [-f FILE] [-ct COUNTRY] [-ef]
                              [--age-min AGE_MIN] [--age-max AGE_MAX]
                              [--age-step AGE_STEP]

optional arguments:
  -h, --help            show this help message and exit
  -f FILE, --file FILE  The tab separated file that will be exported
  -ct COUNTRY, --country COUNTRY
                        The country code for example JP for Japan.
  -ef, --exclude-female
                        All females will be exluded by default
  --age-min AGE_MIN     The minimal age
  --age-max AGE_MAX     The maximum age
  --age-step AGE_STEP   The step between age_min and age_max
```

## Pre-requisites

For Ubuntu 14.04, you have to update the pip
```
wget https://bootstrap.pypa.io/get-pip.py
sudo python get-pip.py
```

Then install the dependencies

```
pip3 install facebookads
pip3 install facepy
```

## Get long-lived access token

You can refer to this article: [Obtaining Never-expiring Access_token to Post on Facebook Page](http://blog.lwolf.org/blog/2014/06/16/obtaining-never-expiring-access-token-to-post-on-facebook-page/)

### Step 1. Get a short lived access token

* Open [Facebook API Explorer](https://developers.facebook.com/tools/explorer/)
* Select the given application
* Select the proper permissions (ads_management, ads_read, read_insights etc)
* Press the button 'Get Access Token'

### Step 2. Get a long-lived access token

Construct a CURL request like that 

```
curl -d "https://graph.facebook.com/oauth/access_token?client_id=<my_app_id>&client_secret=<my_app_secret>&grant_type=fb_exchange_token&fb_exchange_token=<short-lived-access_token>"
```

The 'curl' response will include the new long-lived (60 days) access token and its expiration date.

### Step 3. Get a never-expire access token

Go to [Facebook Explorer Tool](https://developers.facebook.com/tools/explorer)

Send requests to ```/v2.0/me/accounts```. In the response JSON, you will find a ```access_token```. Please copy it.

Go to [Facebook AccessToken Tool](https://developers.facebook.com/tools/debug/accesstoken)

Submit your copied access token, you will see ```Expires:Never``` in the response.

## Install

Make a configuration file

```
[Authentication]
app_id = <facebook app id>
app_secret = <facebook app secret>
access_token = <facebook access token>

[Defaults]
ad_account = <facebook ads account id>

[Email]
# Note: SMTP SHOULD SUPPORT SSL
email_sender = <sender@mail.com>
# You can specify multi receivers by ','
# For example: 
#   email_receiver = user1@mail.com,user2@mail.com
email_receiver = <receiver@mail.com>
email_smtpserver = <smtp.mail.com>
email_username = <sender@mail.com>
email_password = <password>
email_port = <port>

[JSONStore]
# Use JSON to store data
```
