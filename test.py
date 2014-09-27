from instagram.client import InstagramAPI
import passwords
import json
import flask
import random
import time

IMAGES_JSON = "images.json"

def find_image_by_url(images, url):
    for image in images:
        if image["url"] == url:
            return image
    return None

def poll_instagram():
    images = json.load(open(IMAGES_JSON))
    api = InstagramAPI(access_token=passwords.ACCESS_TOKEN)
    tag_media, next = api.tag_recent_media(tag_name="krisandbrad", count=5)
    print len(tag_media)
    for media in tag_media:
        url = media.images['standard_resolution'].url
        image = find_image_by_url(images, url)
        if image is None:
            images.append({
                "url": url,
                "deleted": False,
                "lastDisplayed": 0,
            })
            print "Adding " + url

    f = open(IMAGES_JSON, "w")
    json.dump(images, f)
    f.close()

app = flask.Flask(__name__)
# app.debug = True

@app.route("/")
def index():
    return flask.render_template("index.html")

@app.route("/random")
def random_image():
    poll_instagram()
    images = json.load(open(IMAGES_JSON))
    images = [image for image in images if not image["deleted"]]
    if len(images) == 0:
        flask.abort(404)
        return

    images.sort(key=lambda image: image["lastDisplayed"])
    image = images[0]
    image["lastDisplayed"] = time.time()
    f = open(IMAGES_JSON, "w")
    json.dump(images, f)
    f.close()
    url = image["url"]
    return flask.redirect(url)

def main():
    app.run(host='0.0.0.0')

if __name__ == "__main__":
    main()
