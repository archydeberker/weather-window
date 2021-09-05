import actions
from app_factory import create_app


def main(email: str):

    actions.delete_user(email)

    actions


if __name__ == '__main__':

    app = create_app()
    app.app_context().push()

    email = 'pierre.faille@elementai.com'
    main(email)
