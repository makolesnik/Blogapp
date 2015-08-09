from selenium import webdriver
import unittest
import warnings

class NewVisitorTest(unittest.TestCase):

    BASE_URL = "http://127.0.0.1:8000/"
 
    def setUp(self):
	self.browser = webdriver.Chrome("Tools/chromedriver")
	self.browser.implicitly_wait(3)
	  

    def tearDown(self):
	self.browser.quit()

    def test_can_start_blogging(self):
	self.browser.get(self.BASE_URL)
	
	self.assertIn ("Blog",  self.browser.title, "Browser title was " + self.browser.title)

    def test_entry_title_in_browser_title(self):
	self.browser.get(self.BASE_URL+"1/")
	entry_title = self.browser.find_element_by_css_selector('article h2 a')
	self.assertIn(entry_title.text, self.browser.title)

    def test_entry_text_is_short_on_the_homepage(self):
	self.browser.get(self.BASE_URL)
	entry_text = self.browser.find_element_by_css_selector(
	' div.large-8.columns article p:nth-child(4)')
	self.assertTrue(len(entry_text.text) <= 255, "Entry text is not short")


    def test_nav_is_present(self):
	self.browser.get(self.BASE_URL+"1/")
	nav = self.browser.find_element_by_name('nav')
	
	#options = ['Blog', 'All entries']
	self.assertIn('Blog', nav.text)
	self.assertIn('All entries', nav.text)

    def test_active_nav_option_is_shown_active(self):
	self.browser.get(self.BASE_URL)
	option = self.browser.find_element_by_name('option-all-entries')
	self.assertIn('active', option.get_attribute('class'))

    def test_not_active_nav_option_is_not_shown_active(self):
	self.browser.get(self.BASE_URL+"1/")
        option = self.browser.find_element_by_name('option-all-entries')
        self.assertNotIn('active', option.get_attribute('class'))



if __name__ == '__main__':
    unittest.main()
