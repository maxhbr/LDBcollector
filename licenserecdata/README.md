Due to the file size limit on GitHub, please download the dataset at [here](https://figshare.com/s/3a098d0249693061cd93).

And you need to import it into MongoDB. Run:

```
mongorestore --db=license --gzip data/package.bson.gz
mongorestore --db=libraries --gzip data/projects.bson.gz
```