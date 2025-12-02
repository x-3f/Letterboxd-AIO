from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time

class LetterboxdUnfollower:
    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.driver = None
        self.following = set()
        self.followers = set()
        
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
            # Wait for and fill login form
            username_field = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "field-username"))
            )
            password_field = self.driver.find_element(By.ID, "field-password")
            
            username_field.send_keys(self.username)
            password_field.send_keys(self.password)
            
            # Try multiple possible submit button selectors
            submit_selectors = [
                "button[type='submit']",
                "input[type='submit']",
                "button.button.-action",
                ".button.-action.-green"
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
                print("Could not find submit button, trying form submit...")
                password_field.submit()
            else:
                submit_btn.click()
            
            # Wait for login to complete
            time.sleep(3)
            
            # Check if login was successful by looking for profile link
            if self.username.lower() in self.driver.current_url.lower():
                print("Login successful!")
                return True
            
            # Alternative check - look for signed-in indicator
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
    
    def get_all_users_from_page(self):
        """Extract all usernames from the current page using multiple methods"""
        usernames = set()
        
        # Method 1: Extract from person-summary divs with avatar links
        try:
            person_divs = self.driver.find_elements(By.CSS_SELECTOR, "div.person-summary")
            for person in person_divs:
                try:
                    avatar_link = person.find_element(By.CSS_SELECTOR, "a.avatar")
                    href = avatar_link.get_attribute("href")
                    if href:
                        username = href.strip("/").split("/")[-1]
                        if username and username != "":
                            usernames.add(username)
                except:
                    pass
        except:
            pass
        
        # Method 2: Extract from table rows with name links
        try:
            name_links = self.driver.find_elements(By.CSS_SELECTOR, "a.name")
            for link in name_links:
                href = link.get_attribute("href")
                if href:
                    username = href.strip("/").split("/")[-1]
                    if username and username != "":
                        usernames.add(username)
        except:
            pass
        
        return usernames
    
    def load_all_pages_by_url(self, base_url):
        """Load all pages by directly navigating to page URLs"""
        all_users = set()
        page = 1
        
        while True:
            url = f"{base_url}page/{page}/" if page > 1 else base_url
            print(f"Loading page {page}...")
            self.driver.get(url)
            time.sleep(2)
            
            # Get users from this page
            page_users = self.get_all_users_from_page()
            
            if not page_users:
                # No users found, we've reached the end
                break
            
            all_users.update(page_users)
            print(f"  Found {len(page_users)} users on page {page} (Total: {len(all_users)})")
            
            # Check if there's a next page link
            try:
                next_link = self.driver.find_element(By.CSS_SELECTOR, "a.next")
                page += 1
            except NoSuchElementException:
                # No next page, we're done
                break
        
        return all_users
    
    def get_following(self):
        """Get list of users you follow"""
        print("\n" + "="*50)
        print("Getting following list...")
        print("="*50)
        
        base_url = f"https://letterboxd.com/{self.username}/following/"
        self.following = self.load_all_pages_by_url(base_url)
        
        print(f"\nTotal following: {len(self.following)} users")
        return self.following
    
    def get_followers(self):
        """Get list of users who follow you"""
        print("\n" + "="*50)
        print("Getting followers list...")
        print("="*50)
        
        base_url = f"https://letterboxd.com/{self.username}/followers/"
        self.followers = self.load_all_pages_by_url(base_url)
        
        print(f"\nTotal followers: {len(self.followers)} users")
        return self.followers
    
    def unfollow_non_followers(self, delay=3):
        """Unfollow users who don't follow you back"""
        non_followers = self.following - self.followers
        
        if not non_followers:
            print("\n" + "="*50)
            print("Everyone you follow follows you back!")
            print("="*50)
            return
        
        print("\n" + "="*50)
        print(f"Found {len(non_followers)} users who don't follow you back")
        print("="*50)
        print("Starting unfollow process...\n")
        
        unfollowed_count = 0
        failed_users = []
        
        for i, user in enumerate(non_followers, 1):
            try:
                # Go to user's profile
                self.driver.get(f"https://letterboxd.com/{user}/")
                time.sleep(1.5)
                
                # Find the unfollow button - use the correct selector
                try:
                    unfollow_btn = WebDriverWait(self.driver, 5).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, "a.js-button-following"))
                    )
                    unfollow_btn.click()
                    
                    unfollowed_count += 1
                    print(f"✓ Unfollowed: {user} ({i}/{len(non_followers)})")
                    
                    # Delay between unfollows to avoid rate limiting
                    time.sleep(delay)
                    
                except TimeoutException:
                    print(f"✗ Could not find unfollow button for {user} ({i}/{len(non_followers)})")
                    failed_users.append(user)
                
            except Exception as e:
                error_msg = str(e)[:80]
                print(f"✗ Failed to unfollow {user}: {error_msg} ({i}/{len(non_followers)})")
                failed_users.append(user)
        
        print("\n" + "="*50)
        print("SUMMARY")
        print("="*50)
        print(f"Successfully unfollowed: {unfollowed_count}/{len(non_followers)} users")
        if failed_users:
            print(f"Failed to unfollow: {len(failed_users)} users")
            print(f"Failed users: {', '.join(failed_users[:10])}")
            if len(failed_users) > 10:
                print(f"  ... and {len(failed_users) - 10} more")
        print("="*50)
    
    def run(self, delay_between_unfollows=3):
        """Main execution flow"""
        try:
            self.setup_driver()
            
            if not self.login():
                return
            
            time.sleep(2)
            
            self.get_following()
            self.get_followers()
            
            self.unfollow_non_followers(delay=delay_between_unfollows)
            
        except Exception as e:
            print(f"\nError during execution: {e}")
        
        finally:
            if self.driver:
                input("\nPress Enter to close browser...")
                self.driver.quit()



if __name__ == "__main__":
    # Configuration
    USERNAME = "x"  # Replace with your Letterboxd username
    PASSWORD = "x"  # Replace with your Letterboxd password
    
    # Delay between unfollows (in seconds) - increase if you get rate limited
    DELAY = 3
    
    print("="*50)
    print("Letterboxd Unfollow Non-Followers")
    print("="*50)
    
    unfollower = LetterboxdUnfollower(USERNAME, PASSWORD)
    unfollower.run(delay_between_unfollows=DELAY)
