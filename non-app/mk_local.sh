
        """
        with open('/stocks/.my.env','w') as fh:
            for x in ['AUTH0_CLIENT_ID', 'AUTH0_CLIENT_SECRET', 'AUTH0_DOMAIN', 'APP_SECRET_KEY', 'collection','database', 'mongohost', 'mongousername', 'port']:
                fh.write(f"{x}={mysecret[x]}\n")
        """

