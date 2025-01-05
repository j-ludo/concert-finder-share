import os
import sys
import glob
import shutil

def cleanup():
    """Remove all authentication and cache files."""
    files_removed = []
    
    # List of files and patterns to clean up
    cleanup_items = [
        '.cache*',              # Spotify cache files
        'token.pickle',         # Google Calendar token
        '*.pyc',               # Python cache files
        '__pycache__',         # Python cache directory
    ]
    
    print("Starting cleanup...")
    
    for item in cleanup_items:
        matches = glob.glob(item)
        for match in matches:
            try:
                if os.path.isdir(match):
                    shutil.rmtree(match)
                else:
                    os.remove(match)
                files_removed.append(match)
            except Exception as e:
                print(f"Error removing {match}: {e}")
    
    if files_removed:
        print("\nRemoved the following files/directories:")
        for file in files_removed:
            print(f"- {file}")
        print("\nCleanup complete! You'll need to re-authenticate when you next run the program.")
    else:
        print("\nNo files needed to be cleaned up.")

def safe_cleanup():
    """Interactive cleanup with confirmation."""
    print("This will remove all cached credentials and authentication data.")
    print("You'll need to re-authenticate with Google and Spotify after cleanup.")
    
    while True:
        response = input("\nDo you want to proceed? (yes/no): ").lower().strip()
        if response in ['yes', 'y']:
            cleanup()
            break
        elif response in ['no', 'n']:
            print("Cleanup cancelled.")
            break
        else:
            print("Please answer 'yes' or 'no'")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == '--force':
        cleanup()
    else:
        safe_cleanup()
