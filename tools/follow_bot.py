from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time

class LetterboxdFollowBot:
    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.driver = None
        
    def setup_driver(self):
        """Initialize Chrome driver with options"""
        options = webdriver.ChromeOptions()
        options.add_argument('--start-maximized')
        options.add_argument('--disable-blink-features=AutomationControlled')
        self.driver = webdriver.Chrome(options=options)
        
    def login(self):
        """Login to Letterboxd"""
        print("Logging in...")
        self.driver.get("https://letterboxd.com/sign-in/")
        
        try:
            username_field = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "field-username"))
            )
            password_field = self.driver.find_element(By.ID, "field-password")
            
            username_field.send_keys(self.username)
            password_field.send_keys(self.password)
            
            submit_selectors = [
                "button[type='submit']",
                "input[type='submit']",
                "button.button.-action"
            ]
            
            submit_btn = None
            for selector in submit_selectors:
                try:
                    submit_btn = self.driver.find_element(By.CSS_SELECTOR, selector)
                    if submit_btn:
                        break
                except NoSuchElementException:
                    continue
            
            if not submit_btn:
                password_field.submit()
            else:
                submit_btn.click()
            
            time.sleep(3)
            
            try:
                self.driver.find_element(By.CSS_SELECTOR, "a.avatar")
                print("Login successful!")
                return True
            except NoSuchElementException:
                print("Login may have failed - please check credentials")
                return False
            
        except Exception as e:
            print(f"Login failed: {e}")
            return False
    
    def get_users_from_page(self):
        """Extract all usernames from the current page"""
        usernames = []
        
        try:
            person_divs = self.driver.find_elements(By.CSS_SELECTOR, "div.person-summary")
            for person in person_divs:
                try:
                    avatar_link = person.find_element(By.CSS_SELECTOR, "a.avatar")
                    href = avatar_link.get_attribute("href")
                    if href:
                        username = href.strip("/").split("/")[-1]
                        if username and username != "" and username != self.username:
                            usernames.append(username)
                except:
                    pass
        except:
            pass
        
        # Fallback method
        try:
            name_links = self.driver.find_elements(By.CSS_SELECTOR, "a.name")
            for link in name_links:
                href = link.get_attribute("href")
                if href:
                    username = href.strip("/").split("/")[-1]
                    if username and username != "" and username != self.username and username not in usernames:
                        usernames.append(username)
        except:
            pass
        
        return usernames
    
    def follow_user(self, username):
        """Follow a specific user"""
        try:
            self.driver.get(f"https://letterboxd.com/{username}/")
            time.sleep(1.5)
            
            # Look specifically for the follow button with the correct classes
            try:
                # First check if already following
                already_following = self.driver.find_elements(By.CSS_SELECTOR, "button.js-button-following, a.js-button-following")
                if already_following and any(btn.is_displayed() for btn in already_following):
                    return None  # Already following
                
                # Find the follow button
                follow_buttons = self.driver.find_elements(By.CSS_SELECTOR, "button.js-button-follow, a.js-button-follow")
                
                follow_btn = None
                for btn in follow_buttons:
                    if btn.is_displayed():
                        follow_btn = btn
                        break
                
                if not follow_btn:
                    return False  # Button not found
                
                # Click using JavaScript to avoid any overlay issues
                self.driver.execute_script("arguments[0].click();", follow_btn)
                time.sleep(1)
                
                # Verify it worked by checking if button changed to following
                verify_buttons = self.driver.find_elements(By.CSS_SELECTOR, "button.js-button-following, a.js-button-following")
                if any(btn.is_displayed() for btn in verify_buttons):
                    return True  # Successfully followed
                else:
                    return False  # Click didn't work
                    
            except Exception as e:
                return False
            
        except Exception as e:
            return False
    
    def follow_users_from_target(self, target_username, max_follows=None, delay=2):
        """Follow users from a target user's following list"""
        print("\n" + "="*50)
        print(f"Following users from @{target_username}")
        print("="*50)
        
        base_url = f"https://letterboxd.com/{target_username}/following/"
        page = 1
        total_followed = 0
        total_skipped = 0
        
        while True:
            # Check if we've reached the max follows
            if max_follows and total_followed >= max_follows:
                print(f"\nReached maximum follow limit: {max_follows}")
                break
            
            # Navigate to the page
            url = f"{base_url}page/{page}/" if page > 1 else base_url
            print(f"\n📄 Loading page {page}...")
            self.driver.get(url)
            time.sleep(2)
            
            # Get users from this page
            page_users = self.get_users_from_page()
            
            if not page_users:
                print("No more users found. Finished!")
                break
            
            print(f"Found {len(page_users)} users on page {page}")
            
            # Follow users from this page
            for i, user in enumerate(page_users, 1):
                # Check if we've reached the max follows
                if max_follows and total_followed >= max_follows:
                    print(f"\n✓ Reached maximum follow limit: {max_follows}")
                    break
                
                print(f"  [{i}/{len(page_users)}] Attempting to follow @{user}...", end=" ")
                
                success = self.follow_user(user)
                
                if success is True:
                    total_followed += 1
                    print(f"✓ Followed! (Total: {total_followed})")
                elif success is None:
                    total_skipped += 1
                    print(f"⊝ Already following")
                else:
                    total_skipped += 1
                    print(f"✗ Error (button not found)")
                
                # Delay between follows
                time.sleep(delay)
            
            # Check if we should continue to next page
            if max_follows and total_followed >= max_follows:
                break
            
            # Check if there's a next page
            try:
                self.driver.find_element(By.CSS_SELECTOR, "a.next")
                page += 1
            except NoSuchElementException:
                print("\nNo more pages. Finished!")
                break
        
        print("\n" + "="*50)
        print("SUMMARY")
        print("="*50)
        print(f"Successfully followed: {total_followed} users")
        print(f"Skipped: {total_skipped} users")
        print("="*50)
    
    def run(self, target_username, max_follows=None, delay_between_follows=2):
        """Main execution flow"""
        try:
            self.setup_driver()
            
            if not self.login():
                return
            
            time.sleep(2)
            
            self.follow_users_from_target(target_username, max_follows, delay_between_follows)
            
        except Exception as e:
            print(f"\nError during execution: {e}")
        
        finally:
            if self.driver:
                input("\nPress Enter to close browser...")
                self.driver.quit()


if __name__ == "__main__":
    # Configuration
    YOUR_USERNAME = "your_username"  # Your Letterboxd username
    YOUR_PASSWORD = "your_password"  # Your Letterboxd password
    
    TARGET_USER = "jackhoward"  # The user whose following list you want to copy
    MAX_FOLLOWS = 50  # Maximum number of users to follow (None = unlimited)
    DELAY = 2  # Delay between follows in seconds (increase if rate limited)
    
    print("="*50)
    print("Letterboxd Follow Bot")
    print("="*50)
    print(f"Target User: @{TARGET_USER}")
    print(f"Max Follows: {MAX_FOLLOWS if MAX_FOLLOWS else 'Unlimited'}")
    print("="*50)
    
    bot = LetterboxdFollowBot(YOUR_USERNAME, YOUR_PASSWORD)
    bot.run(TARGET_USER, max_follows=MAX_FOLLOWS, delay_between_follows=DELAY)