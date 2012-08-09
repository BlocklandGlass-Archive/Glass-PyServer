from twisted.internet.defer import inlineCallbacks, DeferredList
from twisted.web.client import getPage
from twisted.python import log

import os
import hashlib
import sqlite3


class CallbackWithInfo(object):
    def __init__(self, *args, **kwargs):
        self.__args = args
        self.__kwargs = kwargs

    def __call__(self, callback):
        def inner(*args, **kwargs):
            target_args = self.__args + args
            target_kwargs = self.__kwargs.copy()
            target_kwargs.update(kwargs)
            callback(*target_args, **target_kwargs)
        return inner


def getUserAgent():
    return "blocklandWIN/2.0"  # TODO, add detection for macs and get the appropriate user agent in that case


def parseManifest(manifest):
    downloadBase = None
    files = []

    for i in manifest.splitlines(False):
        if not i.strip():
            continue

        path, hash = (j.strip() for j in i.split('\t'))

        if path == "DOWNLOADURL":
            downloadBase = hash  # Actually the path in this particular case
        else:
            files.append((path, hash))

    return [(downloadBase + "/" + hash, path.lstrip('/'), hash) for (path, hash) in files]


@inlineCallbacks
def updateFromManifests(target, *manifests):
    conn = sqlite3.connect(target + 'cache.db')
    conn.execute("""
        CREATE TABLE IF NOT EXISTS blobs(hash STRING PRIMARY KEY, data BLOB);
    """)
    conn.commit()

    downloadedManifests = []
    for i in manifests:
        manifest = yield getPage(str(i), agent=getUserAgent())
        downloadedManifests.append(manifest)

    parsedManifests = []
    for i in downloadedManifests:
        parsedManifests.append(parseManifest(manifest))

    files = {}
    for manifest in parsedManifests:
        for downloadPath, path, hash in manifest:
            files[hash] = (downloadPath, path)

    checkedFiles = []
    with conn as cursor:
        for hash in files:
            downloadPath, path = files[hash]
            result = cursor.execute("SELECT hash FROM blobs WHERE hash LIKE ?", (hash,)).fetchone()  # = should work, no clue why it doesn't, but this works
            if result != (hash,):
                print hash
                print result
                print hash == result
                checkedFiles.append((downloadPath, hash, path))

    chunkSize = 50
    dlFiles = checkedFiles
    while dlFiles:
        chunk = dlFiles[:chunkSize]
        dlFiles = dlFiles[chunkSize:]
        dlDefs = []
        for downloadPath, hash, path in chunk:
            deferred = getPage(downloadPath)

            @deferred.addCallback
            @CallbackWithInfo(hash)
            def saveFileToCache(targetHash, data):
                with conn as cursor:
                    if cursor.execute("SELECT hash FROM blobs WHERE hash LIKE ?", (targetHash,)).fetchone() != None:
                        print targetHash
                        cursor.execute("UPDATE blobs SET data=? WHERE hash LIKE ?", (buffer(data), targetHash,))
                    else:
                        print targetHash
                        cursor.execute("INSERT INTO blobs(hash, data) VALUES(?, ?)", (targetHash, buffer(data),))
                    cursor.commit()

            @deferred.addErrback
            @CallbackWithInfo(hash)
            def whoops(targetHash, failure):
                log.err(failure, "Download of file with hash '%s' failed, retrying" % targetHash)
                dlFiles.append((downloadPath, targetHash, path))

            dlDefs.append(deferred)
        yield DeferredList(dlDefs)
    conn.commit()

    with conn as cursor:
        for hash in files:
            downloadPath, path = files[hash]
            outPath = target + path
            outPathDir = os.path.dirname(outPath)
            if os.path.exists(outPath):
                sha1 = hashlib.sha1()
                with open(outPath, "rb") as inFile:
                    sha1.update(inFile.read())
                if sha1.hexdigest() == hash:
                    continue

            if not os.path.exists(outPathDir):
                os.makedirs(outPathDir)

            with open(outPath, "wb") as outFile:
                outFile.write(cursor.execute("SELECT data FROM blobs WHERE hash LIKE ?", (hash,)).fetchone()[0])
