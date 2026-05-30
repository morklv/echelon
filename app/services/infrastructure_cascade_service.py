from app import models

def apply_cascade_effects(db, direct_assets):

    cascaded_assets = []
    visited_asset_ids = set()
    
    queue = []

    for asset in direct_assets:

        queue.append({
            "asset_id": asset["id"],
            "source_asset_id": asset["id"],
            "depth": 0,
            "reason": "Connected to directly affected infrastructure"
        })

        visited_asset_ids.add(asset["id"])

    while queue:

        current = queue.pop(0)

        dependencies = db.query(models.InfrastructureDependency).filter(
            models.InfrastructureDependency.source_asset_id == current["asset_id"]
        ).all()

        for dependency in dependencies:

            dependent_asset = db.query(models.InfrastructureAsset).filter(
                models.InfrastructureAsset.id == dependency.dependent_asset_id
            ).first()

            if dependent_asset is None:
                continue

            if dependent_asset.id in visited_asset_ids:
                continue

            visited_asset_ids.add(dependent_asset.id)

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

            queue.append({
                "asset_id": dependent_asset.id,
                "source_asset_id": dependency.source_asset_id,
                "depth": current["depth"] + 1,
                "reason": dependency.description
            })

    return cascaded_assets