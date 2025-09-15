## To release a new version of ipyevents on PyPI:

+ Update `_version.py` (set release version, remove 'dev'), `package.json` and `src/version.ts`
+ git add the _version.py file and git commit
+ `hatch build`
+ `twine upload dist/ipyevents*`
+ `git tag -a X.X.X -m 'comment'`
+ Update _version.py (add 'dev' and increment minor)
+ git add and git commit
+ git push
+ git push --tags

## To release a new version of ipyevents on NPM:

```
# clean out the `dist` and `node_modules` directories
git clean -fdx
npm install
npm run build
npm publish
```
