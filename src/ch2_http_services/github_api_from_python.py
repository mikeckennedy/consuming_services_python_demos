import requests


def main():
    # mikeckennedy
    # consuming_services_python_demos

    user, repo = get_repo_info()

    url = 'https://api.github.com/repos/{}/{}'.format(
        user, repo
    )

    resp = requests.get(url)

    if resp.status_code != 200:
        print("Error accessing repo: {}".format(resp.status_code))
        return

    repo_data = resp.json()
    clone = repo_data.get('clone_url', 'ERROR: NO DATA')

    print("To clone {}'s repo named {}".format(user, repo))
    print("The command is: ")
    print()
    print("git clone {}".format(clone))


def get_repo_info():
    user = input("What is the username? ").strip()
    repo = input("What is the repo name? ").strip()

    return user, repo


if __name__ == '__main__':
    main()
