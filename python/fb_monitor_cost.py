from facebookads.api import FacebookAdsApi
from facebookads import objects
import argparse
import sys, os, datetime, traceback
import fb_config, fb_notification, fb_store

"""
	KEY for the persistent storage.
"""
KEY_LASTSPENT = 'fb_ads_lastspent'


class FBMonitor:

	def __init__(self, configfile=None):
		self.config = fb_config.FBConfig(configfile).config
		self.account_id = 'act_' + self.config.get('Defaults', 'ad_account')
		auth_info = (
		    self.config.get('Authentication', 'app_id'),
		    self.config.get('Authentication', 'app_secret'),
		    self.config.get('Authentication', 'access_token')
		    )
		FacebookAdsApi.init(*auth_info)

		self.store = fb_store.FBStore(self.config)
		self.notify = fb_notification.FBNotify(self.config)

	"""
		Check the total spent on Facebook account
	"""
	def checkSpending(self, alarmMode, threshold):
		try:
			my_account = objects.AdAccount(self.account_id)
			my_account.remote_read(fields=[
				objects.AdAccount.Field.amount_spent,
				objects.AdAccount.Field.balance,
				objects.AdAccount.Field.daily_spend_limit,
				objects.AdAccount.Field.spend_cap,
				])
			total_spent = my_account[objects.AdAccount.Field.amount_spent]/100
			last_spent = self.store.getProperty(KEY_LASTSPENT)
			if ( last_spent is None ):
				last_spent = total_spent
			diff_spent = total_spent - last_spent
			# Store the current spent
			self.store.setProperty(KEY_LASTSPENT, total_spent)
			self.store.store()
			balance = my_account[objects.AdAccount.Field.balance]/100
			daily_spend_limit = my_account[objects.AdAccount.Field.daily_spend_limit]/100
			spend_cap = my_account[objects.AdAccount.Field.spend_cap]
			now = datetime.datetime.now()
			now_str = datetime.date.strftime(now, '%Y-%m-%d %H:%M:%S')
			if alarmMode:
				if threshold>0 and diff_spent>=threshold:
					subject = "[ALARM]Facebook spent ${diff_spent:.2f} is over ${threshold:.2f} on {now}".format(
						total_spent=total_spent, now=now_str, diff_spent=diff_spent, threshold=threshold)
					content = "Facebook total spent: ${:.2f}<br>".format(total_spent) \
						+ "Facebook last spent: ${:.2f}<br>".format(last_spent) \
						+ "Facebook diff spent: ${:.2f}<br>".format(diff_spent) \
						+ "Facebook daily_spend_limit: ${:.2f}<br>".format(daily_spend_limit) \
						+ "Facebook spend_cap: ${:.2f}<br>".format(spend_cap)
					self.notify.notifyByEmail(subject, content)
			else:	
				subject = "Facebook spent ${total_spent:.2f}, spent ${diff_spent:.2f} on {now}".format(
					total_spent=total_spent, now=now_str, diff_spent=diff_spent)
				content = "Facebook total spent: ${:.2f}<br>".format(total_spent) \
					+ "Facebook last spent: ${:.2f}<br>".format(last_spent) \
					+ "Facebook diff spent: ${:.2f}<br>".format(diff_spent) \
					+ "Facebook daily_spend_limit: ${:.2f}<br>".format(daily_spend_limit) \
					+ "Facebook spend_cap: ${:.2f}<br>".format(spend_cap)
				self.notify.notifyByEmail(subject, content)
		except Exception as err:
			traceback.print_tb(err)

if __name__ == '__main__':
	parser = argparse.ArgumentParser(description='Facebook Spending Monitor')
	parser.add_argument('-c', '--config', help="The absoluate path to configuration file.")
	extgroup = parser.add_mutually_exclusive_group(required=True)
	extgroup.add_argument('-m', '--monitor', action='store_true', help='Monitor facebook spending and send message to reveicers')
	extgroup.add_argument('-a', '--alarm', action='store_true', help='Monitor facebook spending and notify receivers only when the spending is above the threshold')
	parser.add_argument('-t', '--threshold', help="Specify the threshold that 'alarm' mode will check. ")
	args = parser.parse_args()
	monitor = None
	if args.config:
		configfile = args.config
		print('configfile:', configfile)
		monitor = FBMonitor(configfile)
	else:
		monitor = FBMonitor()
	if args.threshold:
		threshold = args.threshold
		print('threshold:', threshold)
	if args.monitor:
		monitor.checkSpending(False, 0)
	elif args.alarm:
		monitor.checkSpending(True, threshold)
