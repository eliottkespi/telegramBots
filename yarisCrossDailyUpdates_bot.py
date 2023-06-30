import sys
import logging
from telegram.ext import Application, CommandHandler

# Enable logging
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)

# TODO: exception handling, helper, args, etc...
with open('token') as f:
    lines = f.readlines()
    BOT_TOKEN = lines[0].strip()

if not BOT_TOKEN:
	sys.exit('No bot token found')


# Store the list of subscribed chat IDs
subscribed_chat_ids = []

async def sendDailyUpdate(context):
	await context.bot.send_message(chat_id=context.job.chat_id, text=uglyGetText(), parse_mode='MarkdownV2')

async def start(update, context):
	await update.message.reply_text('/subscribe\n/unsubscribe')

async def subscribe(update, context):
	chat_id = update.effective_message.chat_id

	if chat_id in subscribed_chat_ids:
		await update.message.reply_text('You are already subscribed!')

	else:
		subscribed_chat_ids.append(chat_id)
		context.job_queue.run_repeating(sendDailyUpdate, 5, chat_id=chat_id, name=chat_id)
		await update.message.reply_text('You are now subscribed!')

async def unsubscribe(update, context):
	chat_id = update.effective_message.chat_id

	if chat_id in subscribed_chat_ids:
		subscribed_chat_ids.remove(chat_id)
		context.job_queue.get_jobs_by_name(chat_id)[0].schedule_removal()
		await update.message.reply_text('You are now unsubscribed!')

	else:
		await update.message.reply_text('You are not subscribed!')

def main():
	# Create the Application and pass it your bot's token.
	application = Application.builder().token(BOT_TOKEN).build()

	application.add_handler(CommandHandler("start", start))
	application.add_handler(CommandHandler('subscribe', subscribe))
	application.add_handler(CommandHandler("unsubscribe", unsubscribe))

	# Start the bot
	application.run_polling()

def uglyGetText():
	from selenium import webdriver
	from selenium.webdriver.common.keys import Keys
	from selenium.webdriver.common.by import By
	from selenium.webdriver.support.wait import WebDriverWait
	from selenium.webdriver.common.action_chains import ActionChains
	from selenium.webdriver.support import expected_conditions as EC
	from selenium.webdriver.chrome.options import Options

	chrome_options = Options()
	chrome_options.add_argument('--headless')
	chrome_options.add_argument('window-size=1920x1480')

	BASE_URL = 'https://www.toyota-select.co.il/'
	URL = BASE_URL + '%D7%AA%D7%95%D7%A6%D7%90%D7%95%D7%AA?page=0&limit=20&top_model_id[0]=22'
	driver = webdriver.Chrome(options=chrome_options)
	driver.get(URL)

	try:
		WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "cars-list-wrapper")))

	except Exception as e:
		print('Error')
		print(e)
		return

	finally:
		# driver.quit()

		options = []

		for carCard in driver.find_elements(By.CSS_SELECTOR, 'div.oneCard > a'):
			ActionChains(driver).key_down(Keys.COMMAND).click(carCard).key_up(Keys.COMMAND).perform()

		optionWindowHandles = driver.window_handles[1:]

		for optionWindowHandle in optionWindowHandles:
			driver.switch_to.window(optionWindowHandle)
			WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "property-card-content")))

			for propertyCard in driver.find_elements(By.CSS_SELECTOR, '.property-card-content'):
				propertyTitle = propertyCard.find_element(By.CSS_SELECTOR, 'h6.property-title').text
				propertyText = propertyCard.find_element(By.CSS_SELECTOR, 'h3.property-text').text

				if propertyTitle == 'קילומטר':
					km = propertyText
				elif propertyTitle == 'שנת ייצור':
					year = propertyText

			price = driver.find_element(By.CSS_SELECTOR, 'div.full-price-wrapper > span.price').text



			options.append({ 'url': driver.current_url, 'km': km, 'year': year, 'price': price })

		text = '*Daily Update*\n\n'

		for option in options:
			text += 'Price: {}\nKM: {}\nYear: {}\n[Link]({})\n\n'.format(option['price'], option['km'], option['year'], option['url'])

		return text



if __name__ == '__main__':
	main()

