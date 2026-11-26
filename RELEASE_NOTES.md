# Release notes

## 0.3.21

### Fixed
- **README documented wrong environment variable names.** The *Environment variables* section of `README.md` listed `MYIPAM_APP_ID` and `MYIPAM_PASSWORD`, but `ipamServer` reads `MYIPAM_APPID` and `MYIPAM_PASSWD`, which are also the names used by the clients and test scripts. The README now uses the names of the code and documents `MYIPAM_CACERT`.
- **The `token` argument of `ipamServer()` was ignored.** The constructor read `MYIPAM_TOKEN` but never replaced it with the `token` argument, so the `--ipam-token` option of `ipamcli`, `ipam2text`, `ipamScanAgent` and `esxinfrcli` had no effect. The argument now overrides the environment variable, like the other connection parameters.
- **The `app_id` argument of `ipamServer()` was applied under the wrong condition.** The code did `if url: self.app_id = app_id` instead of `if app_id:`, so giving `--ipam-url` without `--ipam-appid` cleared the value read from `MYIPAM_APPID`, and giving `--ipam-appid` without `--ipam-url` was ignored. The argument now overrides the environment variable only when it is given.
