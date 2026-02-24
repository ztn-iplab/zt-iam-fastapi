import math
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy.orm import Session

from app.api_key import require_api_key
from app.db import get_db
from app.models import AigDecisionLog, AigObservation, RealTimeLog, TelecomEvent, Tenant
from utils.location import get_ip_location

router = APIRouter(prefix="/api/v1/aig", tags=["AIg"])


def _parse_dt(value: str | None) -> datetime | None:
    if not value:
        return None
    raw = value.strip()
    if not raw:
        return None
    if raw.endswith("Z"):
        raw = raw[:-1] + "+00:00"
    try:
        return datetime.fromisoformat(raw)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid datetime format: {value}",
        ) from exc


def _coerce_bool(value, default: bool = False) -> bool:
    if value is None:
        return default
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return bool(value)
    if isinstance(value, str):
        return value.strip().lower() in {"1", "true", "yes", "y"}
    return default


def _coerce_float(value):
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError) as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid numeric value: {value}",
        ) from exc


def _coerce_int(value):
    if value is None or value == "":
        return None
    try:
        return int(value)
    except (TypeError, ValueError) as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid integer value: {value}",
        ) from exc


def _clamp01(value: float) -> float:
    return max(0.0, min(1.0, float(value)))


def _build_telecom_event(
    item: dict,
    tenant: Tenant,
) -> TelecomEvent:
    event_type = (item.get("event_type") or "").strip()
    if not event_type:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="event_type is required",
        )

    event_time = _parse_dt(item.get("event_time")) or datetime.utcnow()
    ingested_at = _parse_dt(item.get("ingested_at")) or datetime.utcnow()

    metadata_json = item.get("metadata_json")
    if metadata_json is not None and not isinstance(metadata_json, (dict, list)):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="metadata_json must be an object or array if provided",
        )

    user_id = item.get("user_id")
    tenant_id = item.get("tenant_id") or tenant.id
    try:
        user_id = int(user_id) if user_id not in (None, "") else None
        tenant_id = int(tenant_id) if tenant_id not in (None, "") else tenant.id
    except (TypeError, ValueError) as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="user_id and tenant_id must be integers when provided",
        ) from exc

    return TelecomEvent(
        tenant_id=tenant_id,
        user_id=user_id,
        mobile_number=item.get("mobile_number"),
        iccid=item.get("iccid"),
        old_iccid=item.get("old_iccid"),
        new_iccid=item.get("new_iccid"),
        network_provider=item.get("network_provider"),
        event_type=event_type,
        event_time=event_time,
        ingested_at=ingested_at,
        source_type=(item.get("source_type") or "internal").strip() or "internal",
        source_ref=item.get("source_ref"),
        source_independent=_coerce_bool(item.get("source_independent"), default=False),
        source_confidence=_coerce_float(item.get("source_confidence")),
        source_weight_hint=_coerce_float(item.get("source_weight_hint")),
        correlation_id=item.get("correlation_id"),
        experiment_run_id=item.get("experiment_run_id"),
        actor_label=item.get("actor_label"),
        metadata_json=metadata_json,
    )


def _validate_json_blob(name: str, value):
    if value is not None and not isinstance(value, (dict, list)):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"{name} must be an object or array if provided",
        )
    return value


def _build_aig_observation(item: dict, tenant: Tenant) -> AigObservation:
    source_family = (item.get("source_family") or "").strip()
    source_name = (item.get("source_name") or "").strip()
    signal_key = (item.get("signal_key") or "").strip()
    if not source_family or not source_name or not signal_key:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="source_family, source_name, and signal_key are required",
        )

    evidence_value = _coerce_float(item.get("evidence_value"))
    if evidence_value is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="evidence_value is required")
    if evidence_value < 0 or evidence_value > 1:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="evidence_value must be in [0,1]")

    tenant_id = _coerce_int(item.get("tenant_id")) or tenant.id
    user_id = _coerce_int(item.get("user_id"))
    observed_at = _parse_dt(item.get("observed_at")) or datetime.utcnow()
    ingested_at = _parse_dt(item.get("ingested_at")) or datetime.utcnow()

    return AigObservation(
        tenant_id=tenant_id,
        user_id=user_id,
        observed_at=observed_at,
        ingested_at=ingested_at,
        source_family=source_family,
        source_name=source_name,
        signal_key=signal_key,
        evidence_value=evidence_value,
        weight=_coerce_float(item.get("weight")),
        reliability=_coerce_float(item.get("reliability")),
        session_id=item.get("session_id"),
        session_label=item.get("session_label"),
        correlation_id=item.get("correlation_id"),
        experiment_run_id=item.get("experiment_run_id"),
        actor_label=item.get("actor_label"),
        action_name=item.get("action_name"),
        resource_type=item.get("resource_type"),
        resource_id=item.get("resource_id"),
        metadata_json=_validate_json_blob("metadata_json", item.get("metadata_json")),
    )


def _build_aig_decision(item: dict, tenant: Tenant) -> AigDecisionLog:
    action_name = (item.get("action_name") or "").strip()
    decision = (item.get("decision") or "").strip().lower()
    if not action_name:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="action_name is required")
    if decision not in {"allow", "step_up", "deny"}:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="decision must be one of: allow, step_up, deny",
        )

    tenant_id = _coerce_int(item.get("tenant_id")) or tenant.id
    user_id = _coerce_int(item.get("user_id"))
    decision_time = _parse_dt(item.get("decision_time")) or datetime.utcnow()
    ingested_at = _parse_dt(item.get("ingested_at")) or datetime.utcnow()

    return AigDecisionLog(
        tenant_id=tenant_id,
        user_id=user_id,
        decision_time=decision_time,
        ingested_at=ingested_at,
        action_name=action_name,
        action_class=item.get("action_class"),
        resource_type=item.get("resource_type"),
        resource_id=item.get("resource_id"),
        session_id=item.get("session_id"),
        correlation_id=item.get("correlation_id"),
        experiment_run_id=item.get("experiment_run_id"),
        actor_label=item.get("actor_label"),
        c_obs=_coerce_float(item.get("c_obs")),
        c_decay=_coerce_float(item.get("c_decay")),
        c_value=_coerce_float(item.get("c_value")),
        threshold=_coerce_float(item.get("threshold")),
        alpha=_coerce_float(item.get("alpha")),
        decay_lambda=_coerce_float(item.get("decay_lambda")),
        delta_t_seconds=_coerce_float(item.get("delta_t_seconds")),
        decision=decision,
        reason=item.get("reason"),
        step_up_required=_coerce_bool(item.get("step_up_required"), default=(decision == "step_up")),
        observation_count=_coerce_int(item.get("observation_count")),
        metadata_json=_validate_json_blob("metadata_json", item.get("metadata_json")),
    )


def _select_observations_for_authorize(
    db: Session,
    tenant_id: int,
    *,
    user_id: int | None,
    session_id: str | None,
    correlation_id: str | None,
    experiment_run_id: str | None,
    window_seconds: int,
) -> list[AigObservation]:
    q = db.query(AigObservation).filter(AigObservation.tenant_id == tenant_id)
    if user_id is not None:
        q = q.filter(AigObservation.user_id == user_id)
    # For AIg continuity, correlation_id is the primary session trace key across
    # heterogeneous sources (e.g., HMS browser session_id may differ).
    if correlation_id:
        q = q.filter(AigObservation.correlation_id == correlation_id)
    elif session_id:
        q = q.filter(AigObservation.session_id == session_id)
    if experiment_run_id:
        q = q.filter(AigObservation.experiment_run_id == experiment_run_id)

    lower = datetime.utcnow() - timedelta(seconds=max(0, window_seconds))
    q = q.filter(AigObservation.observed_at >= lower)
    return q.order_by(AigObservation.observed_at.desc(), AigObservation.id.desc()).all()


def _latest_prior_decision(
    db: Session,
    tenant_id: int,
    *,
    user_id: int | None,
    session_id: str | None,
    correlation_id: str | None,
    action_name: str | None,
) -> AigDecisionLog | None:
    q = db.query(AigDecisionLog).filter(AigDecisionLog.tenant_id == tenant_id)
    if user_id is not None:
        q = q.filter(AigDecisionLog.user_id == user_id)
    if session_id:
        q = q.filter(AigDecisionLog.session_id == session_id)
    if correlation_id:
        q = q.filter(AigDecisionLog.correlation_id == correlation_id)
    if action_name:
        q = q.filter(AigDecisionLog.action_name == action_name)
    return q.order_by(AigDecisionLog.decision_time.desc(), AigDecisionLog.id.desc()).first()


@router.post("/telecom/events")
def ingest_telecom_event(
    payload: dict,
    request: Request,
    db: Session = Depends(get_db),
    tenant: Tenant = Depends(require_api_key),
):
    event = _build_telecom_event(payload, tenant)
    db.add(event)
    db.flush()

    db.add(
        RealTimeLog(
            user_id=event.user_id,
            tenant_id=tenant.id,
            action=f"AIg telecom event ingested: {event.event_type}",
            ip_address=request.client.host if request.client else None,
            device_info=request.headers.get("User-Agent", ""),
            location=get_ip_location(request.client.host if request.client else None),
            risk_alert=False,
        )
    )
    db.commit()
    return {
        "status": "ok",
        "event_id": event.id,
        "tenant_id": event.tenant_id,
        "event_type": event.event_type,
        "event_time": event.event_time.isoformat(),
    }


@router.post("/telecom/events/batch")
def ingest_telecom_events_batch(
    payload: dict,
    request: Request,
    db: Session = Depends(get_db),
    tenant: Tenant = Depends(require_api_key),
):
    items = payload.get("events")
    if not isinstance(items, list) or not items:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="events must be a non-empty array",
        )

    created = []
    for item in items:
        if not isinstance(item, dict):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Each event in events must be an object",
            )
        event = _build_telecom_event(item, tenant)
        db.add(event)
        db.flush()
        created.append(event)

    db.add(
        RealTimeLog(
            user_id=None,
            tenant_id=tenant.id,
            action=f"AIg telecom batch ingested ({len(created)} events)",
            ip_address=request.client.host if request.client else None,
            device_info=request.headers.get("User-Agent", ""),
            location=get_ip_location(request.client.host if request.client else None),
            risk_alert=False,
        )
    )
    db.commit()

    return {
        "status": "ok",
        "count": len(created),
        "event_ids": [e.id for e in created],
    }


@router.get("/telecom/events")
def list_telecom_events(
    limit: int = Query(default=50, ge=1, le=500),
    user_id: int | None = Query(default=None),
    correlation_id: str | None = Query(default=None),
    event_type: str | None = Query(default=None),
    db: Session = Depends(get_db),
    tenant: Tenant = Depends(require_api_key),
):
    q = db.query(TelecomEvent).filter(TelecomEvent.tenant_id == tenant.id)
    if user_id is not None:
        q = q.filter(TelecomEvent.user_id == user_id)
    if correlation_id:
        q = q.filter(TelecomEvent.correlation_id == correlation_id)
    if event_type:
        q = q.filter(TelecomEvent.event_type == event_type)

    rows = q.order_by(TelecomEvent.event_time.desc(), TelecomEvent.id.desc()).limit(limit).all()
    return {
        "count": len(rows),
        "events": [
            {
                "id": row.id,
                "tenant_id": row.tenant_id,
                "user_id": row.user_id,
                "event_type": row.event_type,
                "event_time": row.event_time.isoformat() if row.event_time else None,
                "ingested_at": row.ingested_at.isoformat() if row.ingested_at else None,
                "mobile_number": row.mobile_number,
                "iccid": row.iccid,
                "old_iccid": row.old_iccid,
                "new_iccid": row.new_iccid,
                "network_provider": row.network_provider,
                "source_type": row.source_type,
                "source_ref": row.source_ref,
                "source_independent": row.source_independent,
                "source_confidence": row.source_confidence,
                "source_weight_hint": row.source_weight_hint,
                "correlation_id": row.correlation_id,
                "experiment_run_id": row.experiment_run_id,
                "actor_label": row.actor_label,
                "metadata_json": row.metadata_json,
            }
            for row in rows
        ],
    }


@router.post("/observations")
def ingest_aig_observation(
    payload: dict,
    request: Request,
    db: Session = Depends(get_db),
    tenant: Tenant = Depends(require_api_key),
):
    row = _build_aig_observation(payload, tenant)
    db.add(row)
    db.flush()
    db.add(
        RealTimeLog(
            user_id=row.user_id,
            tenant_id=tenant.id,
            action=f"AIg observation ingested: {row.source_family}/{row.signal_key}",
            ip_address=request.client.host if request.client else None,
            device_info=request.headers.get("User-Agent", ""),
            location=get_ip_location(request.client.host if request.client else None),
            risk_alert=False,
        )
    )
    db.commit()
    return {"status": "ok", "observation_id": row.id, "observed_at": row.observed_at.isoformat()}


@router.post("/observations/batch")
def ingest_aig_observations_batch(
    payload: dict,
    request: Request,
    db: Session = Depends(get_db),
    tenant: Tenant = Depends(require_api_key),
):
    items = payload.get("observations")
    if not isinstance(items, list) or not items:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="observations must be a non-empty array")
    rows = []
    for item in items:
        if not isinstance(item, dict):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Each observation must be an object")
        row = _build_aig_observation(item, tenant)
        db.add(row)
        db.flush()
        rows.append(row)
    db.add(
        RealTimeLog(
            user_id=None,
            tenant_id=tenant.id,
            action=f"AIg observation batch ingested ({len(rows)} items)",
            ip_address=request.client.host if request.client else None,
            device_info=request.headers.get("User-Agent", ""),
            location=get_ip_location(request.client.host if request.client else None),
            risk_alert=False,
        )
    )
    db.commit()
    return {"status": "ok", "count": len(rows), "observation_ids": [r.id for r in rows]}


@router.get("/observations")
def list_aig_observations(
    limit: int = Query(default=100, ge=1, le=1000),
    user_id: int | None = Query(default=None),
    correlation_id: str | None = Query(default=None),
    experiment_run_id: str | None = Query(default=None),
    source_family: str | None = Query(default=None),
    signal_key: str | None = Query(default=None),
    db: Session = Depends(get_db),
    tenant: Tenant = Depends(require_api_key),
):
    q = db.query(AigObservation).filter(AigObservation.tenant_id == tenant.id)
    if user_id is not None:
        q = q.filter(AigObservation.user_id == user_id)
    if correlation_id:
        q = q.filter(AigObservation.correlation_id == correlation_id)
    if experiment_run_id:
        q = q.filter(AigObservation.experiment_run_id == experiment_run_id)
    if source_family:
        q = q.filter(AigObservation.source_family == source_family)
    if signal_key:
        q = q.filter(AigObservation.signal_key == signal_key)
    rows = q.order_by(AigObservation.observed_at.desc(), AigObservation.id.desc()).limit(limit).all()
    return {
        "count": len(rows),
        "observations": [
            {
                "id": r.id,
                "tenant_id": r.tenant_id,
                "user_id": r.user_id,
                "observed_at": r.observed_at.isoformat() if r.observed_at else None,
                "ingested_at": r.ingested_at.isoformat() if r.ingested_at else None,
                "source_family": r.source_family,
                "source_name": r.source_name,
                "signal_key": r.signal_key,
                "evidence_value": r.evidence_value,
                "weight": r.weight,
                "reliability": r.reliability,
                "session_id": r.session_id,
                "session_label": r.session_label,
                "correlation_id": r.correlation_id,
                "experiment_run_id": r.experiment_run_id,
                "actor_label": r.actor_label,
                "action_name": r.action_name,
                "resource_type": r.resource_type,
                "resource_id": r.resource_id,
                "metadata_json": r.metadata_json,
            }
            for r in rows
        ],
    }


@router.post("/decisions")
def ingest_aig_decision(
    payload: dict,
    request: Request,
    db: Session = Depends(get_db),
    tenant: Tenant = Depends(require_api_key),
):
    row = _build_aig_decision(payload, tenant)
    db.add(row)
    db.flush()
    db.add(
        RealTimeLog(
            user_id=row.user_id,
            tenant_id=tenant.id,
            action=f"AIg decision logged: {row.action_name} -> {row.decision}",
            ip_address=request.client.host if request.client else None,
            device_info=request.headers.get("User-Agent", ""),
            location=get_ip_location(request.client.host if request.client else None),
            risk_alert=(row.decision != "allow"),
        )
    )
    db.commit()
    return {"status": "ok", "decision_id": row.id, "decision": row.decision}


@router.post("/decisions/batch")
def ingest_aig_decisions_batch(
    payload: dict,
    request: Request,
    db: Session = Depends(get_db),
    tenant: Tenant = Depends(require_api_key),
):
    items = payload.get("decisions")
    if not isinstance(items, list) or not items:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="decisions must be a non-empty array")
    rows = []
    for item in items:
        if not isinstance(item, dict):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Each decision must be an object")
        row = _build_aig_decision(item, tenant)
        db.add(row)
        db.flush()
        rows.append(row)
    db.add(
        RealTimeLog(
            user_id=None,
            tenant_id=tenant.id,
            action=f"AIg decision batch ingested ({len(rows)} items)",
            ip_address=request.client.host if request.client else None,
            device_info=request.headers.get("User-Agent", ""),
            location=get_ip_location(request.client.host if request.client else None),
            risk_alert=False,
        )
    )
    db.commit()
    return {"status": "ok", "count": len(rows), "decision_ids": [r.id for r in rows]}


@router.get("/decisions")
def list_aig_decisions(
    limit: int = Query(default=100, ge=1, le=1000),
    user_id: int | None = Query(default=None),
    correlation_id: str | None = Query(default=None),
    experiment_run_id: str | None = Query(default=None),
    action_name: str | None = Query(default=None),
    decision: str | None = Query(default=None),
    db: Session = Depends(get_db),
    tenant: Tenant = Depends(require_api_key),
):
    q = db.query(AigDecisionLog).filter(AigDecisionLog.tenant_id == tenant.id)
    if user_id is not None:
        q = q.filter(AigDecisionLog.user_id == user_id)
    if correlation_id:
        q = q.filter(AigDecisionLog.correlation_id == correlation_id)
    if experiment_run_id:
        q = q.filter(AigDecisionLog.experiment_run_id == experiment_run_id)
    if action_name:
        q = q.filter(AigDecisionLog.action_name == action_name)
    if decision:
        q = q.filter(AigDecisionLog.decision == decision)
    rows = q.order_by(AigDecisionLog.decision_time.desc(), AigDecisionLog.id.desc()).limit(limit).all()
    return {
        "count": len(rows),
        "decisions": [
            {
                "id": r.id,
                "tenant_id": r.tenant_id,
                "user_id": r.user_id,
                "decision_time": r.decision_time.isoformat() if r.decision_time else None,
                "ingested_at": r.ingested_at.isoformat() if r.ingested_at else None,
                "action_name": r.action_name,
                "action_class": r.action_class,
                "resource_type": r.resource_type,
                "resource_id": r.resource_id,
                "session_id": r.session_id,
                "correlation_id": r.correlation_id,
                "experiment_run_id": r.experiment_run_id,
                "actor_label": r.actor_label,
                "c_obs": r.c_obs,
                "c_decay": r.c_decay,
                "c_value": r.c_value,
                "threshold": r.threshold,
                "alpha": r.alpha,
                "decay_lambda": r.decay_lambda,
                "delta_t_seconds": r.delta_t_seconds,
                "decision": r.decision,
                "reason": r.reason,
                "step_up_required": r.step_up_required,
                "observation_count": r.observation_count,
                "metadata_json": r.metadata_json,
            }
            for r in rows
        ],
    }


@router.get("/traces/export")
def export_aig_trace(
    correlation_id: str | None = Query(default=None),
    experiment_run_id: str | None = Query(default=None),
    user_id: int | None = Query(default=None),
    limit_per_stream: int = Query(default=2000, ge=1, le=10000),
    db: Session = Depends(get_db),
    tenant: Tenant = Depends(require_api_key),
):
    if not correlation_id and not experiment_run_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Provide correlation_id or experiment_run_id",
        )

    telecom_q = db.query(TelecomEvent).filter(TelecomEvent.tenant_id == tenant.id)
    obs_q = db.query(AigObservation).filter(AigObservation.tenant_id == tenant.id)
    dec_q = db.query(AigDecisionLog).filter(AigDecisionLog.tenant_id == tenant.id)

    if user_id is not None:
        telecom_q = telecom_q.filter(TelecomEvent.user_id == user_id)
        obs_q = obs_q.filter(AigObservation.user_id == user_id)
        dec_q = dec_q.filter(AigDecisionLog.user_id == user_id)
    if correlation_id:
        telecom_q = telecom_q.filter(TelecomEvent.correlation_id == correlation_id)
        obs_q = obs_q.filter(AigObservation.correlation_id == correlation_id)
        dec_q = dec_q.filter(AigDecisionLog.correlation_id == correlation_id)
    if experiment_run_id:
        telecom_q = telecom_q.filter(TelecomEvent.experiment_run_id == experiment_run_id)
        obs_q = obs_q.filter(AigObservation.experiment_run_id == experiment_run_id)
        dec_q = dec_q.filter(AigDecisionLog.experiment_run_id == experiment_run_id)

    telecom_rows = (
        telecom_q.order_by(TelecomEvent.event_time.asc(), TelecomEvent.id.asc())
        .limit(limit_per_stream)
        .all()
    )
    obs_rows = (
        obs_q.order_by(AigObservation.observed_at.asc(), AigObservation.id.asc())
        .limit(limit_per_stream)
        .all()
    )
    dec_rows = (
        dec_q.order_by(AigDecisionLog.decision_time.asc(), AigDecisionLog.id.asc())
        .limit(limit_per_stream)
        .all()
    )

    return {
        "tenant_id": tenant.id,
        "filters": {
            "correlation_id": correlation_id,
            "experiment_run_id": experiment_run_id,
            "user_id": user_id,
            "limit_per_stream": limit_per_stream,
        },
        "counts": {
            "telecom_events": len(telecom_rows),
            "observations": len(obs_rows),
            "decisions": len(dec_rows),
        },
        "telecom_events": [
            {
                "id": r.id,
                "user_id": r.user_id,
                "event_type": r.event_type,
                "event_time": r.event_time.isoformat() if r.event_time else None,
                "ingested_at": r.ingested_at.isoformat() if r.ingested_at else None,
                "mobile_number": r.mobile_number,
                "iccid": r.iccid,
                "old_iccid": r.old_iccid,
                "new_iccid": r.new_iccid,
                "network_provider": r.network_provider,
                "source_type": r.source_type,
                "source_ref": r.source_ref,
                "source_independent": r.source_independent,
                "source_confidence": r.source_confidence,
                "source_weight_hint": r.source_weight_hint,
                "correlation_id": r.correlation_id,
                "experiment_run_id": r.experiment_run_id,
                "actor_label": r.actor_label,
                "metadata_json": r.metadata_json,
            }
            for r in telecom_rows
        ],
        "observations": [
            {
                "id": r.id,
                "user_id": r.user_id,
                "observed_at": r.observed_at.isoformat() if r.observed_at else None,
                "ingested_at": r.ingested_at.isoformat() if r.ingested_at else None,
                "source_family": r.source_family,
                "source_name": r.source_name,
                "signal_key": r.signal_key,
                "evidence_value": r.evidence_value,
                "weight": r.weight,
                "reliability": r.reliability,
                "session_id": r.session_id,
                "session_label": r.session_label,
                "correlation_id": r.correlation_id,
                "experiment_run_id": r.experiment_run_id,
                "actor_label": r.actor_label,
                "action_name": r.action_name,
                "resource_type": r.resource_type,
                "resource_id": r.resource_id,
                "metadata_json": r.metadata_json,
            }
            for r in obs_rows
        ],
        "decisions": [
            {
                "id": r.id,
                "user_id": r.user_id,
                "decision_time": r.decision_time.isoformat() if r.decision_time else None,
                "ingested_at": r.ingested_at.isoformat() if r.ingested_at else None,
                "action_name": r.action_name,
                "action_class": r.action_class,
                "resource_type": r.resource_type,
                "resource_id": r.resource_id,
                "session_id": r.session_id,
                "correlation_id": r.correlation_id,
                "experiment_run_id": r.experiment_run_id,
                "actor_label": r.actor_label,
                "c_obs": r.c_obs,
                "c_decay": r.c_decay,
                "c_value": r.c_value,
                "threshold": r.threshold,
                "alpha": r.alpha,
                "decay_lambda": r.decay_lambda,
                "delta_t_seconds": r.delta_t_seconds,
                "decision": r.decision,
                "reason": r.reason,
                "step_up_required": r.step_up_required,
                "observation_count": r.observation_count,
                "metadata_json": r.metadata_json,
            }
            for r in dec_rows
        ],
    }


@router.post("/authorize")
def aig_authorize(
    payload: dict,
    request: Request,
    db: Session = Depends(get_db),
    tenant: Tenant = Depends(require_api_key),
):
    action_name = (payload.get("action_name") or "").strip()
    if not action_name:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="action_name is required")

    user_id = _coerce_int(payload.get("user_id"))
    session_id = payload.get("session_id")
    correlation_id = payload.get("correlation_id")
    experiment_run_id = payload.get("experiment_run_id")
    actor_label = payload.get("actor_label")

    theta = _coerce_float(payload.get("threshold"))
    theta = 0.7 if theta is None else _clamp01(theta)

    alpha = _coerce_float(payload.get("alpha"))
    alpha = 0.7 if alpha is None else _clamp01(alpha)

    decay_lambda = _coerce_float(payload.get("decay_lambda"))
    decay_lambda = 0.02 if decay_lambda is None else max(0.0, float(decay_lambda))

    window_seconds = _coerce_int(payload.get("window_seconds")) or 300
    window_seconds = max(0, window_seconds)

    initial_c = _coerce_float(payload.get("initial_c"))
    initial_c = 1.0 if initial_c is None else _clamp01(initial_c)

    on_below_threshold = (payload.get("on_below_threshold") or "step_up").strip().lower()
    if on_below_threshold not in {"step_up", "deny"}:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="on_below_threshold must be 'step_up' or 'deny'",
        )

    observations = _select_observations_for_authorize(
        db,
        tenant.id,
        user_id=user_id,
        session_id=session_id,
        correlation_id=correlation_id,
        experiment_run_id=experiment_run_id,
        window_seconds=window_seconds,
    )

    prior = _latest_prior_decision(
        db,
        tenant.id,
        user_id=user_id,
        session_id=session_id,
        correlation_id=correlation_id,
        action_name=action_name,
    )
    now = datetime.utcnow()
    c_prev = _clamp01(prior.c_value) if (prior and prior.c_value is not None) else initial_c
    if prior and prior.decision_time:
        dt_seconds = max(0.0, (now - prior.decision_time).total_seconds())
    else:
        dt_seconds = float(_coerce_float(payload.get("delta_t_seconds")) or 0.0)

    c_decay = _clamp01(c_prev * math.exp(-decay_lambda * dt_seconds))

    c_obs = None
    if observations:
        weighted_sum = 0.0
        total_weight = 0.0
        for obs in observations:
            e = _clamp01(obs.evidence_value)
            w = obs.weight if obs.weight is not None else 1.0
            if w is None or w < 0:
                w = 0.0
            weighted_sum += w * e
            total_weight += w
        if total_weight > 0:
            c_obs = _clamp01(weighted_sum / total_weight)
        else:
            c_obs = _clamp01(sum(_clamp01(o.evidence_value) for o in observations) / len(observations))

    if c_obs is None:
        c_value = c_decay
        reason = "no_recent_observations"
    else:
        c_value = _clamp01(alpha * c_obs + (1.0 - alpha) * c_decay)
        reason = "threshold_met" if c_value >= theta else "below_threshold"

    if c_value >= theta:
        decision = "allow"
        step_up_required = False
    else:
        decision = "step_up" if on_below_threshold == "step_up" else "deny"
        step_up_required = decision == "step_up"

    metadata_json = _validate_json_blob("metadata_json", payload.get("metadata_json")) or {}
    metadata_json = {
        **metadata_json,
        "observation_ids_used": [o.id for o in observations],
        "window_seconds": window_seconds,
        "c_prev": c_prev,
    }

    row = AigDecisionLog(
        tenant_id=tenant.id,
        user_id=user_id,
        decision_time=now,
        ingested_at=now,
        action_name=action_name,
        action_class=payload.get("action_class"),
        resource_type=payload.get("resource_type"),
        resource_id=payload.get("resource_id"),
        session_id=session_id,
        correlation_id=correlation_id,
        experiment_run_id=experiment_run_id,
        actor_label=actor_label,
        c_obs=c_obs,
        c_decay=c_decay,
        c_value=c_value,
        threshold=theta,
        alpha=alpha,
        decay_lambda=decay_lambda,
        delta_t_seconds=dt_seconds,
        decision=decision,
        reason=reason if reason != "below_threshold" else (payload.get("reason") or "below_threshold"),
        step_up_required=step_up_required,
        observation_count=len(observations),
        metadata_json=metadata_json,
    )
    db.add(row)
    db.flush()

    db.add(
        RealTimeLog(
            user_id=user_id,
            tenant_id=tenant.id,
            action=f"AIg authorize {action_name}: {decision} (C={c_value:.3f}, th={theta:.3f})",
            ip_address=request.client.host if request.client else None,
            device_info=request.headers.get("User-Agent", ""),
            location=get_ip_location(request.client.host if request.client else None),
            risk_alert=(decision != "allow"),
        )
    )
    db.commit()

    return {
        "status": "ok",
        "decision_id": row.id,
        "decision": decision,
        "step_up_required": step_up_required,
        "reason": row.reason,
        "c_obs": c_obs,
        "c_decay": c_decay,
        "c_value": c_value,
        "threshold": theta,
        "alpha": alpha,
        "decay_lambda": decay_lambda,
        "delta_t_seconds": dt_seconds,
        "observation_count": len(observations),
        "observation_ids_used": [o.id for o in observations],
    }
