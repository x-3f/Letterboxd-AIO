import os
import sys

# Add tools directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'tools'))

def clear_screen():
    """Clear the terminal screen"""
    os.system('cls' if os.name == 'nt' else 'clear')

def print_header():
    """Print the main header"""
    print("\n" + "="*60)
    print("█░░ █▀▀ ▀█▀ ▀█▀ █▀▀ █▀█ █▄▄ █▀█ ▀▄▀ █▀▄   ▄▀█ █ █▀█")
    print("█▄▄ ██▄ ░█░ ░█░ ██▄ █▀▄ █▄█ █▄█ █░█ █▄▀   █▀█ █ █▄█")
    print("="*60)
    print("         Made by @x3f on Letterboxd and Claude<3")
    print("="*60)

def print_menu():
    """Print the main menu"""
    print("\n📋 OPTIONS")
    print("-" * 60)
    print("1. 🚫 Unfollow Non-Mutuals")
    print("2. 👥 Follow Bot (Copy someone's following)")
    print("3. 📊 Account Statistics	")
    print("4. ⚙️ Settings")
    print("5. ❌ Exit")
    print("-" * 60)

def get_credentials():
    """Get user credentials"""
    print("\n🔐 LOGIN CREDENTIALS")
    print("-" * 60)
    username = input("Letterboxd Username: ").strip()
    password = input("Letterboxd Password: ").strip()
    return username, password

def unfollow_tool():
    """Run the unfollow non-mutuals tool"""
    clear_screen()
    print_header()
    print("\n🚫 UNFOLLOW NON-MUTUALS")
    print("="*60)
    
    username, password = get_credentials()
    
    print("\n⚙️  Configuration")
    print("-" * 60)
    delay = input("Delay between unfollows (seconds) [3]: ").strip()
    delay = int(delay) if delay else 3
    
    print("\n⏳ Starting unfollow process...")
    print("-" * 60)
    
    try:
        from unfollow import LetterboxdUnfollower
        unfollower = LetterboxdUnfollower(username, password)
        unfollower.run(delay_between_unfollows=delay)
    except ImportError:
        print("\n❌ Error: Could not import unfollow tool.")
        print("Make sure 'unfollow.py' exists in the 'tools' folder.")
        input("\nPress Enter to continue...")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        input("\nPress Enter to continue...")

def follow_bot():
    """Run the follow bot tool"""
    clear_screen()
    print_header()
    print("\n👥 FOLLOW BOT")
    print("="*60)
    
    username, password = get_credentials()
    
    print("\n⚙️  Configuration")
    print("-" * 60)
    target = input("Target user to copy following from: ").strip()
    max_follows = input("Max users to follow [50]: ").strip()
    max_follows = int(max_follows) if max_follows else 50
    delay = input("Delay between follows (seconds) [2]: ").strip()
    delay = int(delay) if delay else 2
    
    print("\n⏳ Starting follow bot...")
    print("-" * 60)
    
    try:
        from follow_bot import LetterboxdFollowBot
        bot = LetterboxdFollowBot(username, password)
        bot.run(target, max_follows=max_follows, delay_between_follows=delay)
    except ImportError:
        print("\n❌ Error: Could not import follow bot.")
        print("Make sure 'follow_bot.py' exists in the 'tools' folder.")
        input("\nPress Enter to continue...")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        input("\nPress Enter to continue...")

def check_stats():
    """Check account statistics"""
    clear_screen()
    print_header()
    print("\n📊 ACCOUNT STATISTICS")
    print("="*60)
    
    username, password = get_credentials()
    
    print("\n⏳ Fetching statistics...")
    print("-" * 60)
    
    try:
        from unfollow import LetterboxdUnfollower
        checker = LetterboxdUnfollower(username, password)
        checker.setup_driver()
        
        if not checker.login():
            print("❌ Login failed!")
            input("\nPress Enter to continue...")
            return
        
        print("\n📈 Gathering data...")
        following = checker.get_following()
        followers = checker.get_followers()
        
        mutuals = following & followers
        non_mutuals = following - followers
        
        print("\n" + "="*60)
        print("ACCOUNT STATISTICS")
        print("="*60)
        print(f"👥 Following: {len(following)}")
        print(f"👤 Followers: {len(followers)}")
        print(f"🤝 Mutuals: {len(mutuals)}")
        print(f"🚫 Non-Mutuals: {len(non_mutuals)}")
        print(f"📊 Follow Ratio: {len(following)/len(followers):.2f}" if followers else "📊 Follow Ratio: N/A")
        print("="*60)
        
        checker.driver.quit()
        input("\nPress Enter to continue...")
        
    except ImportError:
        print("\n❌ Error: Could not import required tools.")
        input("\nPress Enter to continue...")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        input("\nPress Enter to continue...")

def settings():
    """Settings menu"""
    clear_screen()
    print_header()
    print("\n⚙️  SETTINGS")
    print("="*60)
    print("\n⚠️  Default Settings:")
    print("-" * 60)
    print("• Unfollow Delay: 3 seconds")
    print("• Follow Delay: 2 seconds")
    print("• Max Follows: 50 users")
    print("-" * 60)
    print("\n💡 Tip: You can adjust these values when running each tool.")
    print("\n⚠️  Rate Limiting:")
    print("If you get temporarily blocked, increase the delays.")
    print("="*60)
    input("\nPress Enter to continue...")

def main():
    """Main program loop"""
    while True:
        clear_screen()
        print_header()
        print_menu()
        
        choice = input("\nSelect an option (1-5): ").strip()
        
        if choice == "1":
            unfollow_tool()
        elif choice == "2":
            follow_bot()
        elif choice == "3":
            check_stats()
        elif choice == "4":
            settings()
        elif choice == "5":
            clear_screen()
            print("\n👋 Thanks for using Letterboxd AIO!")
            print("="*60)
            sys.exit(0)
        else:
            print("\n❌ Invalid option. Please try again.")
            input("\nPress Enter to continue...")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        clear_screen()
        print("\n\n👋 Interrupted by user. Goodbye!")
        print("="*60)
        sys.exit(0)
