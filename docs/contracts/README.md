# Cross-service contracts

Interfaces between two or more services. When services communicate, the contract lives here rather
than in either repository, so neither owns it and both can diff it.

## `nodes_api_v1.yml`

The node ↔ server wire contract, currently **1.1.1**. Three independent implementations depend on
it: the server in `retina-server`, the node client in `retina-node`, and the conformance harness.

**It is versioned, not frozen.** The changelog at the top of the file is authoritative. A change is
a coordinated event rather than a silent edit: bump the version, record the change in the changelog,
and tell whoever is mid-build. If you find a genuine error in it, raise it rather than working
around it locally.

Superseded versions are kept in `contract-history/` so a change can be diffed.

### Why it lives here now

It previously sat at the root of the `owl` meta-workspace, which is not a git repository. The file
therefore had no history: no way to review a change, and no commit to cite when one landed. The
version number in the changelog was a convention held by the people working on it rather than
anything enforced. Tracked as [86cb2d059](https://app.clickup.com/t/86cb2d059).

Moving it here gives it review, history and a citable commit. The copy under `~/owl` is now a
working copy; **this is the one to edit**.
