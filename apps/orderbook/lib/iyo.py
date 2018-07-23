import  requests
import jose
from jose.jwt import get_unverified_claims

s = requests.session()


class Iyo(object):
    @staticmethod
    def get_user(jwt):
        """
        Verify JWT is valid and return user info
        Return It's You online User from JWT
        :param jwt: JWT token
        :type jwt: str
        :return: user info {'username': 'blah', 'email': 'blah'}
        :rtype: dict
        """

        try:
            claims = get_unverified_claims(jwt)
        except jose.exceptions.JWTError:
            raise RuntimeError('JWT: Invalid')

        username = claims.get("globalid", None) or claims.get("username", None)

        if username is None:
            raise RuntimeError('JWT: can not retrieve username')

        url = "https://itsyou.online/api/users/{}/info".format(username)

        response = s.get(
            url,
            headers={
                'Authorization': 'bearer {}'.format(jwt)
            }
        )

        if response.status_code == 200:
            info = response.json()
            emails = [record['emailaddress'] for record in info['emailaddresses']]

            if not emails:
                raise RuntimeError('JWT: can not retrieve email')

            return {
                'username': username,
                'email': emails[0]
            }
        else:
            raise RuntimeError('JWT: Invalid')
