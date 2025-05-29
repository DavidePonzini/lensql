from server import create_app, start_cleanup_thread


start_cleanup_thread()

app = create_app()

# app.run(
#     host='0.0.0.0',
#     debug=True
# )

