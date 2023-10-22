import os
import instaloader

from dotenv import load_dotenv
from ExecutionAuthorizer import ExecutionAuthorizer


def get_instagram_data(username, tracked_username):
    # Create an Instaloader instance
    il = instaloader.Instaloader()

    try:
        # Login to Instagram
        il.load_session_from_file(username)
    except FileNotFoundError:
        # Request the firefox procedure because there is no session file
        print("Session file does not exist - execute the following procedure:")
        print("1) Login to Instagram in Firefox")
        print("2) Run import_firefox_session.py")
        exit(0)

    # Get your profile
    profile = instaloader.Profile.from_username(il.context, username)

    # Initialize tracked username profile
    tracked_username_profile = next((f for f in profile.get_followees() if f.username == tracked_username), None)

    # Exit if the tracked username profile wasn't found
    if tracked_username_profile is None:
        print("Tracked username ({}) NOT found".format(tracked_username))
        exit(0)

    # Create the lists
    new_followers_list = tracked_username_profile.get_followers()
    new_following_list = tracked_username_profile.get_followees()

    return new_followers_list, new_following_list


def create_files():
    open('followers.txt', 'w')
    open('following.txt', 'w')

    open('followers_new.txt', 'w')
    open('following_new.txt', 'w')

    open('followers_lost.txt', 'w')
    open('following_lost.txt', 'w')


def initialize_files(followers, following):
    with open('followers.txt', 'w') as followers_file:
        for follower in followers:
            followers_file.write(follower.username + '\n')

    with open('following.txt', 'w') as following_file:
        for followed in following:
            following_file.write(followed.username + '\n')


def compare_and_write_lists(new_list, old_list, new_file_name, lost_file_name):
    new_items = set(new_list) - set(old_list)
    lost_items = set(old_list) - set(new_list)

    with open(new_file_name, 'a') as new_file:
        for item in new_items:
            new_file.write(item + '\n')

    with open(lost_file_name, 'a') as lost_file:
        for item in lost_items:
            lost_file.write(item + '\n')


if __name__ == '__main__':

    authorizer = ExecutionAuthorizer()

    authorized, remaining_time = authorizer.authorize_execution()

    if not authorized:
        print("Not enough time has passed to execute the program.")
        print("Time remaining: {}".format(remaining_time))
        exit(0)

    # TODO: make EnvironmentManager (it shall ask to enter username and tracked username if env doesn't exist)
    # Load local variables from .env file
    load_dotenv()

    instagram_username = os.getenv('INSTAGRAM_USERNAME')
    instagram_tracked_username = os.getenv('INSTAGRAM_TRACKED_USERNAME')

    # TODO: make DataGrabber
    # Get instagram data
    new_followers, new_following = get_instagram_data(instagram_username, instagram_tracked_username)

    # TODO: make FileManager
    # TODO: followers shall be classified in friends and fans
    # TODO: followings shall be classified in friends and non-follow-back
    # Create and initialize files if they don't exist
    if not (os.path.isfile('followers.txt') or os.path.isfile('following.txt') or
            os.path.isfile('followers_new.txt') or os.path.isfile('following_new.txt') or
            os.path.isfile('followers_lost.txt') or os.path.isfile('following_lost.txt')):
        create_files()
        initialize_files(new_followers, new_following)
        print("Files created and initialized.")

    # Load the existing followers and following lists
    with open('followers.txt', 'r') as followers_file:
        existing_followers = followers_file.read().splitlines()

    with open('following.txt', 'r') as following_file:
        existing_following = following_file.read().splitlines()

    # Compare the lists and save the results
    compare_and_write_lists(new_followers, existing_followers, 'followers_new.txt', 'followers_lost.txt')
    compare_and_write_lists(new_following, existing_following, 'following_new.txt', 'following_lost.txt')

    # TODO: write logic to print numbers
    print("Data update complete.")
    print("\tFollowers: {} ({} new, {} lost)")
    print("\tFollowing: {} ({} new, {} lost)")
