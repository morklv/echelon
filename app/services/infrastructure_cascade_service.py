from app import models
# imports database models


def apply_cascade_effects(db, direct_assets):
    # finds downstream assets connected to directly affected assets

    cascaded_assets = []
    # stores cascade-affected assets

    visited_asset_ids = set()
    # prevents infinite loops in graph cycles

    queue = []
    # assets whose outgoing dependency edges still need to be checked

    for asset in direct_assets:
        # loops through directly affected nearby assets

        queue.append({
            "asset_id": asset["id"],
            "source_asset_id": asset["id"],
            "depth": 0,
            "reason": "Connected to directly affected infrastructure"
        })
        # starts graph traversal from direct asset

        visited_asset_ids.add(asset["id"])
        # marks direct asset as already visited

    while queue:
        # continues until all connected downstream assets are checked

        current = queue.pop(0)
        # gets next asset to process

        dependencies = db.query(models.InfrastructureDependency).filter(
            models.InfrastructureDependency.source_asset_id == current["asset_id"]
        ).all()
        # gets all dependency edges starting from current asset

        for dependency in dependencies:
            # loops through downstream dependency edges

            dependent_asset = db.query(models.InfrastructureAsset).filter(
                models.InfrastructureAsset.id == dependency.dependent_asset_id
            ).first()
            # loads downstream connected asset

            if dependent_asset is None:
                continue
            # skips broken dependency rows

            if dependent_asset.id in visited_asset_ids:
                continue
            # prevents duplicate/circular cascade entries

            visited_asset_ids.add(dependent_asset.id)
            # marks connected asset as visited

            cascaded_assets.append({
                "asset_id": dependent_asset.id,
                "asset_type": dependent_asset.asset_type,
                "new_status": "AT_RISK",
                "reason": dependency.description or "Affected through dependency graph.",
                "source_asset_id": dependency.source_asset_id,
                "source_asset_name": current.get("source_asset_name"),
                "dependency_type": dependency.dependency_type,
                "cascade_depth": current["depth"] + 1
            })
            # records cascade impact

            queue.append({
                "asset_id": dependent_asset.id,
                "source_asset_id": dependency.source_asset_id,
                "depth": current["depth"] + 1,
                "reason": dependency.description
            })
            # continues graph traversal from this dependent asset

    return cascaded_assets
    # returns all graph-connected cascade impacts