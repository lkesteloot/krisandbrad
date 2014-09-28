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

def get_deleted():
    urls = open("blacklist").readlines()
    urls = [url.strip() for url in urls]
    return set(urls)

def add_image(images, url):
    print "Adding " + url
    images.append({
        "url": url,
        "deleted": False,
        "lastDisplayed": 0,
    })

def load_images():
    try:
        images = json.load(open(IMAGES_JSON))
    except IOError as e:
        images = []

    original = open("original").readlines()
    original = ["http://plunk.org/~lk/krisandbrad/" + filename.strip() for filename in original]

    if find_image_by_url(images, original[0]) is None:
        for url in original:
            add_image(images, url)

    deleted = get_deleted()
    for image in images:
        if image["url"] in deleted:
            image["deleted"] = True

    return images

def save_images(images):
    f = open(IMAGES_JSON, "w")
    json.dump(images, f, indent=4)
    f.close()

def poll_instagram():
    images = load_images()
    api = InstagramAPI(access_token=passwords.ACCESS_TOKEN)
    changed = False
    tag_media, next = api.tag_recent_media(tag_name="krisandbrad", count=20)
    for media in tag_media:
        url = media.images['standard_resolution'].url
        image = find_image_by_url(images, url)
        if image is None:
            add_image(images, url)
            changed = True
    if changed:
        save_images(images)

app = flask.Flask(__name__)
# app.debug = True

@app.route("/")
def index():
    return flask.render_template("index.html")

@app.route("/random")
def random_image():
    poll_instagram()
    images = load_images()
    images = [image for image in images if not image["deleted"]]
    if len(images) == 0:
        flask.abort(404)
        return

    images.sort(key=lambda image: image["lastDisplayed"])
    image = images[0]
    image["lastDisplayed"] = time.time()
    save_images(images)
    url = image["url"]
    print "Redirecting to " + url
    return flask.redirect(url)

@app.route("/all")
def all_images():
    images = load_images()
    images = [image for image in images if image["url"].find("plunk") == -1]
    images.sort(key=lambda image: image["lastDisplayed"], reverse=True)
    return flask.render_template("all.html", images=images)

def main():
    app.run(host='0.0.0.0')

if __name__ == "__main__":
    main()
