# Stdlib
import sys

# External Libraries
from sqlalchemy.engine.url import URL

# Sayonika Internals
from framework.objects import db, loop, redis, sayonika_instance
from framework.settings import SETTINGS


async def setup_db():
    # Set binding for Gino and init Redis
    await db.set_bind(
        URL(
            "postgres",
            username=SETTINGS["DB_USER"],
            password=SETTINGS["DB_PASS"],
            host=SETTINGS["DB_HOST"],
            port=SETTINGS["DB_PORT"],
            database=SETTINGS["DB_NAME"],
        )
    )

    # await redis.setup()


@sayonika_instance.after_serving
async def teardown():
    await sayonika_instance.aioh_sess.close()
    await db.pop_bind().close()
    redis.close()


sayonika_instance.debug = len(sys.argv) > 1 and sys.argv[1] == "--debug"
sayonika_instance.gather("routes")
loop.run_until_complete(setup_db())

# Only run `app.run` if running this file directly - intended for development. Otherwise should use hypercorn.
if __name__ == "__main__":
    try:
        sayonika_instance.run(
            SETTINGS["SERVER_BIND"], int(SETTINGS["SERVER_PORT"]), loop=loop
        )
    except KeyboardInterrupt:
        # Stop big stack trace getting printed when interrupting
        pass
