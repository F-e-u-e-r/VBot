from werkzeug.middleware.proxy_fix import ProxyFix

   # Save original wsgi_app
   original_wsgi_app = app.wsgi_app
   
   # Apply ProxyFix
   app.wsgi_app = ProxyFix(
       app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1
   )
