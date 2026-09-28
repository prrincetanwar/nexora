import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import numpy as np
import networkx as nx
import plotly.graph_objects as go
import platform
import socket
import time
import os
import re
import json
import shutil
import subprocess
import ssl
import uuid
import sys
from datetime import datetime, timedelta
from pathlib import Path
from collections import Counter
try:
    import psutil
except ImportError:
    psutil = None
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

st.set_page_config(
    page_title="NEXORA | Crypto-Agility Orchestration Framework",
    page_icon="🔐",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ============================================================
# NEXORA V28
# Evidence-Driven Crypto-Agility Decision Engine
#
# Controlled laboratory prototype.
# The application demonstrates:
# Discovery -> Crypto Exposure -> ACDKG -> Impact Reasoning
# -> AI Effort Assessment -> Migration Decision -> Simulation
#
# It does NOT modify production infrastructure.
# ============================================================

PQC_PRIMARY = {
    "Digital Signature": "ML-DSA",
    "Key Establishment": "ML-KEM",
}
PQC_OPTIONS = {
    "Digital Signature": ["ML-DSA", "SLH-DSA"],
    # FIPS 203 defines three ML-KEM parameter sets. Showing them here makes
    # key-establishment selection explicit instead of presenting a broken
    # one-item dropdown.
    "Key Establishment": ["ML-KEM-512", "ML-KEM-768", "ML-KEM-1024"],
}
PQC_STANDARD = {
    "ML-KEM": "NIST FIPS 203",
    "ML-KEM-512": "NIST FIPS 203 · parameter set 512",
    "ML-KEM-768": "NIST FIPS 203 · parameter set 768",
    "ML-KEM-1024": "NIST FIPS 203 · parameter set 1024",
    "ML-DSA": "NIST FIPS 204",
    "SLH-DSA": "NIST FIPS 205",
}
ALGORITHM_VULNERABILITY = {"RSA-2048": 5, "RSA-3072": 4, "ECC-P256": 5}

SCENARIOS = {
    "E-Commerce Order Management": {
        "case": "NXR-ECOM-001", "icon": "🛒",
        "summary": "Customer-facing commerce platform connecting web access, order processing, identity, APIs and transaction data.",
        "why": "Customer-facing authentication and API paths make cryptographic changes propagate beyond a single certificate or key.",
        "focus": "Customer access + identity + order API continuity",
        "roles": {
            "web":"Customer Web Portal", "app":"Order Management App", "api":"Order API Server",
            "auth":"Customer Identity Server", "db":"Order Database", "vpn":"Operations VPN Gateway",
            "admin":"Operations Admin Workstation", "ssh":"SSH Administration Service", "legacy":"Legacy Reporting Service",
        },
        "extra_components": [
            ["CACHE-01","Order Session Cache","Service","Running","OpenSSL","TLS"],
        ],
        "assets": [
            ("A01","Customer Portal Certificate","Certificate","RSA-2048","Digital Signature","HTTPS/TLS","web",5,5,3,"External Web Services"),
            ("A02","Order API Certificate","Certificate","RSA-2048","Digital Signature","TLS","api",5,5,4,"Application Services"),
            ("A03","Identity Service Certificate","Certificate","RSA-3072","Digital Signature","TLS/PKI","auth",5,4,5,"Identity & PKI"),
            ("A04","Operations VPN Certificate","Certificate","ECC-P256","Digital Signature","VPN","vpn",4,5,4,"Network Access"),
            ("A05","Order Application Key","Key","ECC-P256","Digital Signature","Internal API","app",3,2,2,"Application Services"),
            ("A06","Order Database Service Key","Key","RSA-3072","Key Establishment","TLS","db",5,3,4,"Data Services"),
            ("A07","SSH Administration Key","Key","RSA-2048","Digital Signature","SSH","ssh",4,4,3,"Administration"),
            ("A08","Legacy Reporting Service Key","Key","RSA-2048","Digital Signature","TLS","legacy",3,2,2,"Legacy Services"),
        ],
        "extra_edges": [
            ("Order Management App","Order Session Cache","depends_on"),
            ("Order Session Cache","TLS","uses_protocol"),
            ("Order API Server","Order Session Cache","communicates_with"),
        ],
    },
    "University Learning & Identity": {
        "case": "NXR-UNIV-001", "icon": "🎓",
        "summary": "University learning and identity environment connecting student access, learning services, SSO, research access and academic records.",
        "why": "Central SSO and academic-record dependencies can propagate cryptographic migration consequences into student-facing and institutional services.",
        "focus": "SSO + student access + academic records",
        "roles": {
            "web":"Student Portal", "app":"Learning Application", "api":"Learning API Server",
            "auth":"University SSO Server", "db":"Student Records Database", "vpn":"Research VPN Gateway",
            "admin":"University Admin Workstation", "ssh":"SSH Administration Service", "legacy":"Legacy Examination Service",
        },
        "extra_components": [
            ["LMS-01","Learning Management Service","Service","Running","OpenSSL","TLS"],
            ["EXAM-01","Examination Delivery Service","Service","Running","OpenSSL","TLS"],
        ],
        "assets": [
            ("A01","Student Portal Certificate","Certificate","ECC-P256","Digital Signature","HTTPS/TLS","web",5,4,3,"Student Services"),
            ("A02","Learning API Certificate","Certificate","RSA-2048","Digital Signature","TLS","api",5,4,4,"Learning Services"),
            ("A03","University SSO Certificate","Certificate","RSA-3072","Digital Signature","TLS/PKI","auth",5,5,5,"Identity & PKI"),
            ("A04","Research VPN Certificate","Certificate","ECC-P256","Digital Signature","VPN","vpn",4,3,4,"Research Access"),
            ("A05","Learning Session Key","Key","RSA-2048","Key Establishment","Internal API","app",4,3,3,"Learning Services"),
            ("A06","Student Records Service Key","Key","RSA-3072","Key Establishment","TLS","db",5,4,5,"Academic Records"),
            ("A07","Administrator SSH Key","Key","RSA-2048","Digital Signature","SSH","ssh",3,2,2,"Administration"),
            ("A08","Legacy Examination Key","Key","RSA-2048","Digital Signature","TLS","legacy",2,1,1,"Legacy Services"),
            ("A09","Learning Management Certificate","Certificate","RSA-2048","Digital Signature","TLS","app",4,3,3,"Learning Services"),
        ],
        "extra_edges": [
            ("Learning Application","Learning Management Service","depends_on"),
            ("Learning Management Service","TLS","uses_protocol"),
            ("Examination Delivery Service","Learning Management Service","depends_on"),
            ("Learning Application","Examination Delivery Service","communicates_with"),
        ],
    },
    "Healthcare Operations Platform": {
        "case": "NXR-HEALTH-001", "icon": "🏥",
        "summary": "Healthcare operations environment connecting patient access, clinical services, hospital identity, remote access and clinical records.",
        "why": "Clinical services, sensitive records and remote access increase the modeled consequence of migration disruption in this controlled environment.",
        "focus": "Clinical identity + records + remote access",
        "roles": {
            "web":"Patient Portal", "app":"Clinical Operations App", "api":"Clinical API Server",
            "auth":"Hospital Identity Server", "db":"Clinical Records Database", "vpn":"Clinical Remote Access Gateway",
            "admin":"Hospital Admin Workstation", "ssh":"SSH Administration Service", "legacy":"Legacy Laboratory Service",
        },
        "extra_components": [
            ["LAB-01","Laboratory Results Service","Service","Running","OpenSSL","TLS"],
            ["PHARM-01","Pharmacy Integration Service","Service","Running","OpenSSL","TLS"],
            ["MON-01","Clinical Monitoring Gateway","Network Device","Running","Crypto Library","VPN"],
        ],
        "assets": [
            ("A01","Patient Portal Certificate","Certificate","RSA-3072","Digital Signature","HTTPS/TLS","web",5,5,4,"Patient Services"),
            ("A02","Clinical API Certificate","Certificate","RSA-3072","Digital Signature","TLS","api",5,5,5,"Clinical Services"),
            ("A03","Hospital Identity Certificate","Certificate","RSA-3072","Digital Signature","TLS/PKI","auth",5,5,5,"Identity & PKI"),
            ("A04","Clinical VPN Certificate","Certificate","ECC-P256","Digital Signature","VPN","vpn",4,3,3,"Remote Access"),
            ("A05","Clinical Application Key","Key","ECC-P256","Digital Signature","Internal API","app",3,2,2,"Clinical Services"),
            ("A06","Clinical Records Key","Key","RSA-3072","Key Establishment","TLS","db",5,4,4,"Clinical Records"),
            ("A07","Administrator SSH Key","Key","RSA-2048","Digital Signature","SSH","ssh",3,2,2,"Administration"),
            ("A08","Legacy Laboratory Service Key","Key","RSA-2048","Digital Signature","TLS","legacy",2,1,1,"Legacy Services"),
            ("A09","Laboratory Results Certificate","Certificate","RSA-2048","Digital Signature","TLS","legacy",4,3,3,"Laboratory Services"),
            ("A10","Pharmacy Integration Key","Key","ECC-P256","Key Establishment","Internal API","api",2,1,2,"Pharmacy Integration"),
        ],
        "extra_edges": [
            ("Clinical Operations App","Laboratory Results Service","depends_on"),
            ("Clinical API Server","Laboratory Results Service","communicates_with"),
            ("Clinical API Server","Pharmacy Integration Service","communicates_with"),
            ("Clinical Remote Access Gateway","Clinical Monitoring Gateway","communicates_with"),
            ("Clinical Monitoring Gateway","VPN","uses_protocol"),
            ("Laboratory Results Service","TLS","uses_protocol"),
            ("Pharmacy Integration Service","Internal API","uses_protocol"),
        ],
    },
}

ROLE_KEYS = ["web","app","api","auth","db","vpn","admin","ssh","legacy"]


# ============================================================
# DATA / ACDKG ENGINE
# ============================================================

def build_scenario_data(name):
    p = SCENARIOS[name]
    names = p["roles"]
    rows = []
    for item in p["assets"]:
        aid, aname, atype, algo, role, protocol, owner_role, crit, exposure, complexity, group = item
        rows.append({
            "id": aid, "name": aname, "type": atype, "algorithm": algo,
            "crypto_role": role, "protocol": protocol, "owner": names[owner_role],
            "criticality": crit, "exposure": exposure, "complexity": complexity,
            "migration_group": group,
        })
    local_df = pd.DataFrame(rows)

    g = nx.DiGraph()
    base_nodes = [
        ("Internet","Network"), (names["web"],"Service"), (names["app"],"Application"),
        (names["api"],"Service"), (names["auth"],"Service"), (names["db"],"Service"),
        (names["vpn"],"Network Device"), (names["admin"],"Endpoint"),
        (names["ssh"],"Service"), (names["legacy"],"Service"),
        ("HTTPS/TLS","Protocol"), ("TLS","Protocol"), ("SSH","Protocol"),
        ("VPN","Protocol"), ("Internal API","Protocol"), ("OpenSSL","Library"),
        ("OpenSSH","Library"), ("PKI","Security Service"),
    ]
    for n,t in base_nodes:
        g.add_node(n,node_type=t)

    edges = [
        (names["web"],"Internet","depends_on"),
        (names["app"],names["web"],"depends_on"),
        (names["app"],names["api"],"depends_on"),
        (names["api"],names["auth"],"depends_on"),
        (names["api"],names["db"],"depends_on"),
        (names["web"],"HTTPS/TLS","uses_protocol"),
        (names["api"],"TLS","uses_protocol"),
        (names["auth"],"TLS","uses_protocol"),
        (names["db"],"TLS","uses_protocol"),
        (names["vpn"],"VPN","uses_protocol"),
        (names["admin"],"SSH","uses_protocol"),
        (names["ssh"],"SSH","uses_protocol"),
        (names["app"],"Internal API","uses_protocol"),
        (names["legacy"],"TLS","uses_protocol"),
        (names["web"],"OpenSSL","uses_library"),
        (names["app"],"OpenSSL","uses_library"),
        (names["api"],"OpenSSL","uses_library"),
        (names["auth"],"OpenSSL","uses_library"),
        (names["db"],"OpenSSL","uses_library"),
        (names["legacy"],"OpenSSL","uses_library"),
        (names["admin"],"OpenSSH","uses_library"),
        (names["ssh"],"OpenSSH","uses_library"),
        (names["auth"],"PKI","protected_by"),
    ]
    edges.extend(p.get("extra_edges", []))
    for a,b,r in edges:
        if a not in g: g.add_node(a,node_type="Component")
        if b not in g: g.add_node(b,node_type="Component")
        g.add_edge(a,b,relation=r)

    owner_role = {r[0]: r[6] for r in p["assets"]}
    for _,row in local_df.iterrows():
        g.add_node(row["id"],node_type="Crypto Asset")
        g.add_edge(names[owner_role[row["id"]]],row["id"],relation="protected_by")
        g.add_node(row["algorithm"],node_type="Crypto Algorithm")
        g.add_edge(row["id"],row["algorithm"],relation="uses_algorithm")

    component_rows = [
        ["OS-01",names["web"],"Service","Running","OpenSSL","HTTPS/TLS"],
        ["APP-01",names["app"],"Application","Running","OpenSSL","Internal API"],
        ["API-01",names["api"],"Service","Running","OpenSSL","TLS"],
        ["AUTH-01",names["auth"],"Service","Running","OpenSSL","TLS/PKI"],
        ["DB-01",names["db"],"Service","Running","OpenSSL","TLS"],
        ["NET-01",names["vpn"],"Network Device","Running","Crypto Library","VPN"],
        ["ADM-01",names["admin"],"Endpoint","Running","OpenSSH","SSH"],
        ["LEG-01",names["legacy"],"Service","Running","OpenSSL","TLS"],
        ["SEC-01","PKI","Security Service","Running","PKI Stack","Certificates"],
    ]
    component_rows.extend(p.get("extra_components", []))
    # Normalize optional scenario extension rows.
    normalized=[]
    for i,r in enumerate(component_rows):
        if len(r)==6: normalized.append(r)
        else: normalized.append([f"EXT-{i+1:02d}",*r])
    components = pd.DataFrame(normalized,columns=["Asset ID","Component","Type","Status","Crypto Dependency","Protocol"])
    return local_df,g,components


df, G, COMPONENTS = build_scenario_data("E-Commerce Order Management")


def direct_owner(asset_id):
    return [s for s,t,d in G.edges(data=True) if t == asset_id and d.get("relation") in {"uses_crypto_asset", "protected_by"}]


def dependency_depths(asset_id):
    depths = {}
    queue = []
    for owner in direct_owner(asset_id):
        depths[owner] = 0
        queue.append(owner)
    while queue:
        cur = queue.pop(0)
        for pred in G.predecessors(cur):
            if G.edges[pred,cur].get("relation") != "depends_on":
                continue
            nd = depths[cur] + 1
            if pred not in depths or nd < depths[pred]:
                depths[pred] = nd
                queue.append(pred)
    return depths


def impacted_components(asset_id):
    return sorted(dependency_depths(asset_id).keys())


def technical_dependencies(asset_id):
    deps = []
    for owner in direct_owner(asset_id):
        for target in G.successors(owner):
            rel = G.edges[owner,target].get("relation")
            if rel in {"uses_protocol","uses_library","uses_service"}:
                deps.append((target,rel))
    return sorted(set(deps))


def asset_paths(asset_id):
    paths = []
    for owner in direct_owner(asset_id):
        paths.append([owner, asset_id])
        queue = [(owner,[owner])]
        visited = {owner}
        while queue:
            cur,path = queue.pop(0)
            for pred in sorted(G.predecessors(cur)):
                if G.edges[pred,cur].get("relation") != "depends_on" or pred in visited:
                    continue
                visited.add(pred)
                npth = [pred] + path
                paths.append(npth + [asset_id])
                queue.append((pred,npth))
    out=[]; seen=set()
    for p in paths:
        k=tuple(p)
        if k not in seen:
            seen.add(k); out.append(p)
    return out


def calculate_cmis(row):
    # NEXORA's project-specific CMIS follows the weighting documented in the
    # implementation plan: vulnerability + dependency impact + criticality +
    # exposure + migration complexity, normalized to 0-100.
    dependency_factor = min(max(len(impacted_components(row["id"])) - 1, 0), 5)
    vulnerability = ALGORITHM_VULNERABILITY.get(row["algorithm"], 2)
    score = (
        vulnerability * 8
        + row["criticality"] * 6
        + row["exposure"] * 5
        + row["complexity"] * 4
        + dependency_factor * 3
    )
    return min(round(score), 100)


def risk_level(score):
    if score >= 81: return "CRITICAL"
    if score >= 61: return "HIGH"
    if score >= 31: return "MODERATE"
    return "LOW"


# ============================================================
# ML ENGINE — CONTROLLED SYNTHETIC DEMONSTRATION
# ============================================================

ML_FEATURES = [
    "criticality","exposure","complexity","dependency_depth",
    "operational_dependents","technical_dependencies","vulnerability"
]


def synthetic_dataset(n=2400, seed=42):
    rng=np.random.default_rng(seed)
    d=pd.DataFrame({
        "criticality":rng.integers(1,6,n),
        "exposure":rng.integers(1,6,n),
        "complexity":rng.integers(1,6,n),
        "dependency_depth":rng.integers(0,5,n),
        "operational_dependents":rng.integers(0,5,n),
        "technical_dependencies":rng.integers(0,4,n),
        "vulnerability":rng.integers(2,6,n),
    })
    def label(r):
        if r.dependency_depth>=3 or (r.criticality>=5 and r.operational_dependents>=3):
            return "CRITICAL"
        if ((r.complexity>=4 and (r.operational_dependents>=2 or r.exposure>=4))
            or (r.dependency_depth>=2 and r.criticality>=4)):
            return "HIGH"
        if r.criticality>=3 or r.exposure>=3 or r.technical_dependencies>=2:
            return "MODERATE"
        return "LOW"
    d["migration_effort"]=d.apply(label,axis=1)
    return d


@st.cache_resource
def train_model():
    data=synthetic_dataset()
    X=data[ML_FEATURES]; y=data["migration_effort"]
    Xtr,Xte,ytr,yte=train_test_split(X,y,test_size=.20,random_state=42,stratify=y)
    model=RandomForestClassifier(n_estimators=220,max_depth=10,random_state=42,class_weight="balanced")
    model.fit(Xtr,ytr)
    return model, accuracy_score(yte,model.predict(Xte))


MODEL, ML_ACCURACY = train_model()


def feature_row(row):
    depths=dependency_depths(row.id)
    max_depth=max(depths.values(),default=0)
    dependents=max(len(depths)-len(direct_owner(row.id)),0)
    return pd.DataFrame([{
        "criticality":row.criticality,
        "exposure":row.exposure,
        "complexity":row.complexity,
        "dependency_depth":max_depth,
        "operational_dependents":dependents,
        "technical_dependencies":len(technical_dependencies(row.id)),
        "vulnerability":ALGORITHM_VULNERABILITY.get(row.algorithm,2)
    }])[ML_FEATURES]


def ml_assess(row):
    x=feature_row(row)
    pred=MODEL.predict(x)[0]
    proba=MODEL.predict_proba(x)[0]
    return pred, round(float(max(proba))*100,1)


def enrich():
    global df
    df["Direct Owner Count"]=df.id.apply(lambda x:len(direct_owner(x)))
    df["Impacted Components"]=df.id.apply(lambda x:len(impacted_components(x)))
    df["Technical Dependencies"]=df.id.apply(lambda x:len(technical_dependencies(x)))
    df["CMIS"]=df.apply(calculate_cmis,axis=1)
    df["Risk"]=df.CMIS.apply(risk_level)
    df["Suggested PQC"]=df.crypto_role.map(PQC_PRIMARY)
    preds=[]; conf=[]
    for _,r in df.iterrows():
        p,c=ml_assess(r); preds.append(p); conf.append(c)
    df["ML Effort"]=preds; df["ML Confidence"]=conf


enrich()


# ============================================================
# DECISION ENGINE
# ============================================================

EFFORT_WEIGHT={"LOW":0,"MODERATE":5,"HIGH":10,"CRITICAL":15}


def decision_signal(row):
    depths=dependency_depths(row.id)
    depth=max(depths.values(),default=0)
    dependents=max(len(depths)-len(direct_owner(row.id)),0)
    # Planning signal is intentionally separate from CMIS: risk, dependency
    # propagation and controlled ML effort jointly influence ordering.
    return round(row.CMIS + depth*3 + dependents*4 + EFFORT_WEIGHT[row["ML Effort"]],1)


def prepare_asset_decision(row):
    tech=technical_dependencies(row.id)
    protocols=[n for n,r in tech if r=="uses_protocol"]
    libs=[n for n,r in tech if r=="uses_library"]
    steps=[
        ("INVENTORY","Confirm the cryptographic asset, owner and current role."),
        ("PKI / KEY PREPARATION",f"Prepare a {row['crypto_role'].lower()} replacement compatible with {row['Suggested PQC']}.")
    ]
    if protocols:
        steps.append(("PROTOCOL VALIDATION","Validate compatibility for: " + ", ".join(protocols) + "."))
    if libs:
        steps.append(("LIBRARY VALIDATION","Validate cryptographic library support: " + ", ".join(libs) + "."))
    if row["type"]=="Certificate" or any(n=="PKI" for n,_ in tech):
        steps.append(("TRUST / PKI VALIDATION","Validate certificate lifecycle, trust-chain and authentication readiness."))
    dependents=max(len(dependency_depths(row.id))-len(direct_owner(row.id)),0)
    if dependents:
        steps.append(("DEPENDENT SERVICE VALIDATION",f"Prepare continuity checks for {dependents} downstream operational dependent(s)."))
    steps.append(("STAGED COMPATIBILITY TEST","Run controlled compatibility and service-continuity validation."))
    steps.append(("MIGRATE",f"Perform the controlled replacement with {row['Suggested PQC']} only after the preparation gates pass."))
    steps.append(("REVALIDATE","Verify dependent services, trust relationships and application behavior; update the inventory."))
    return steps


def strategy_for(row):
    affected=len(impacted_components(row.id))
    if row.Risk=="CRITICAL" or affected>=4:
        return "STAGED MIGRATION"
    if row.Risk=="HIGH" or affected>=2:
        return "DEPENDENCY-AWARE MIGRATION"
    return "CONTROLLED MIGRATION"


def why_first(row):
    deps=max(len(dependency_depths(row.id))-len(direct_owner(row.id)),0)
    depth=max(dependency_depths(row.id).values(),default=0)
    affected=len(impacted_components(row.id))
    return (
        f"This asset is placed early because it has {row['Risk'].lower()} modeled risk, "
        f"{affected} affected component(s), {deps} downstream operational dependent(s), "
        f"and dependency depth {depth}. The order is a prototype planning recommendation, not a production command."
    )


def build_plan():
    rows=[]
    for _,r in df.iterrows():
        rows.append({
            "id":r.id,"name":r["name"],"algorithm":r.algorithm,
            "target":r["Suggested PQC"],"risk":r.Risk,"cmis":r.CMIS,
            "effort":r["ML Effort"],"confidence":r["ML Confidence"],
            "affected":len(impacted_components(r.id)),
            "depth":max(dependency_depths(r.id).values(),default=0),
            "dependents":max(len(dependency_depths(r.id))-len(direct_owner(r.id)),0),
            "signal":decision_signal(r),
        })
    p=pd.DataFrame(rows).sort_values(["signal","cmis"],ascending=False).reset_index(drop=True)
    p["order"]=range(1,len(p)+1)
    p["strategy"]=p.id.apply(lambda x: strategy_for(df.loc[df.id==x].iloc[0]))
    return p


def final_case_finding():
    p=build_plan()
    top=p.iloc[0]
    high=int((df.Risk.isin(["HIGH","CRITICAL"])).sum())
    return top, high


# ============================================================
# SIMULATION
# ============================================================

def simulate(row,target):
    allowed=PQC_OPTIONS.get(row.crypto_role,[])
    if target not in allowed:
        return {
            "status":"BLOCKED",
            "summary":f"{target} does not match the modeled {row.crypto_role.lower()} role. Select a role-compatible PQC target.",
            "risk":"BLOCKED", "checks":[], "affected":[], "paths":[], "conflicts":["Cryptographic role / target mismatch"],
        }
    tech=technical_dependencies(row.id)
    protocols=[n for n,r in tech if r=="uses_protocol"]
    libs=[n for n,r in tech if r=="uses_library"]
    affected=impacted_components(row.id)
    conflicts=[]
    if row["type"]=="Certificate":
        conflicts.append("Certificate / trust-chain compatibility must be validated")
    if protocols:
        conflicts.append("Protocol support must be validated: " + ", ".join(protocols))
    if libs:
        conflicts.append("Library support must be validated: " + ", ".join(libs))
    if len(affected)>=3:
        conflicts.append(f"{len(affected)} operational components are on the modeled impact path")
    checks=[]
    if row["type"]=="Certificate": checks.append("certificate / trust-chain validation")
    if protocols: checks.append("protocol compatibility: "+", ".join(protocols))
    if libs: checks.append("library support: "+", ".join(libs))
    checks.append("dependent service continuity")
    checks.append("post-change inventory and configuration validation")
    if row.CMIS>=81 or len(affected)>=4:
        status="CONDITIONAL — STAGED VALIDATION"
    elif row.CMIS>=61 or len(affected)>=2:
        status="CONDITIONAL — DEPENDENCY VALIDATION"
    else:
        status="CONDITIONAL — CONTROLLED VALIDATION"
    return {
        "status":status,
        "summary":f"{target} is role-compatible with the modeled {row['crypto_role'].lower()} role, but the identified dependencies require validation before any real migration.",
        "risk":row.Risk,
        "checks":checks,
        "affected":affected,
        "paths":asset_paths(row.id),
        "conflicts":conflicts,
    }



# ============================================================
# REAL LOCAL HOST EVIDENCE
# ============================================================


def _run_command(command, timeout=4):
    """Best-effort read-only command runner used only for local evidence fallback."""
    try:
        cp=subprocess.run(command, capture_output=True, text=True, timeout=timeout,
                          shell=isinstance(command,str))
        return cp.stdout.strip()
    except Exception:
        return ""


def _collect_windows_extended_evidence(info):
    """Best-effort Windows-only read-only collection for services, certificate stores and firewall."""
    if platform.system().lower()!="windows":
        return info
    # Running Windows services
    try:
        ps=("Get-Service | Select-Object Name,DisplayName,Status,StartType "
            "| ConvertTo-Json -Compress")
        raw=_run_command(["powershell","-NoProfile","-Command",ps],timeout=8)
        if raw:
            data=json.loads(raw)
            if isinstance(data,dict): data=[data]
            info["service_records"]=[{
                "Name":x.get("Name") or "—","Display Name":x.get("DisplayName") or "—",
                "Status":str(x.get("Status") or "—"),"Start Type":str(x.get("StartType") or "—")
            } for x in (data or [])]
            info["services_count"]=len(info["service_records"])
            info["running_services"]=sum(1 for x in info["service_records"] if str(x["Status"]).lower()=="running")
    except Exception:
        pass
    # Local-machine certificate store inventory. No private key material is exported.
    try:
        ps=("Get-ChildItem Cert:\\LocalMachine\\My | "
            "Select-Object Subject,Thumbprint,NotBefore,NotAfter,HasPrivateKey,"
            "@{N='SignatureAlgorithm';E={$_.SignatureAlgorithm.FriendlyName}} | ConvertTo-Json -Compress")
        raw=_run_command(["powershell","-NoProfile","-Command",ps],timeout=10)
        if raw:
            data=json.loads(raw)
            if isinstance(data,dict): data=[data]
            certs=[]
            for x in data or []:
                certs.append({
                    "Subject":x.get("Subject") or "—","Thumbprint":x.get("Thumbprint") or "—",
                    "Valid From":str(x.get("NotBefore") or "—"),"Valid Until":str(x.get("NotAfter") or "—"),
                    "Private Key":str(x.get("HasPrivateKey") or "False"),
                    "Signature Algorithm":str(x.get("SignatureAlgorithm") or "—")
                })
            info["certificate_records"]=certs
            info["certificate_count"]=len(certs)
    except Exception:
        pass
    # Windows firewall profile status
    try:
        ps=("Get-NetFirewallProfile | Select-Object Name,Enabled,DefaultInboundAction,DefaultOutboundAction "
            "| ConvertTo-Json -Compress")
        raw=_run_command(["powershell","-NoProfile","-Command",ps],timeout=8)
        if raw:
            data=json.loads(raw)
            if isinstance(data,dict): data=[data]
            info["firewall_records"]=[{
                "Profile":x.get("Name") or "—","Enabled":str(x.get("Enabled") or "False"),
                "Inbound":str(x.get("DefaultInboundAction") or "—"),
                "Outbound":str(x.get("DefaultOutboundAction") or "—")
            } for x in (data or [])]
    except Exception:
        pass
    return info

def _windows_fallback_evidence(info):
    """Collect useful Windows evidence when psutil is unavailable.
    This fallback never modifies the machine and never treats local evidence as enterprise discovery.
    """
    # Process inventory through tasklist
    try:
        raw=_run_command(["tasklist","/fo","csv","/nh"], timeout=6)
        rows=[]
        if raw:
            import csv, io
            for r in csv.reader(io.StringIO(raw)):
                if len(r)>=5:
                    mem=re.sub(r"[^0-9]","",r[4])
                    rows.append({"PID":int(r[1]) if r[1].isdigit() else r[1],
                                 "Process":r[0],"Status":"RUNNING",
                                 "Memory MB":round(int(mem)/1024,1) if mem else 0})
        info["process_sample"]=sorted(rows,key=lambda x:float(x.get("Memory MB") or 0),reverse=True)[:20]
        info["processes"]=len(rows)
    except Exception:
        pass

    # CPU count
    try:
        info["cpu_logical"]=os.cpu_count()
    except Exception:
        pass

    # Memory through Windows API when available
    try:
        import ctypes
        class MEMORYSTATUSEX(ctypes.Structure):
            _fields_=[("dwLength",ctypes.c_ulong),("dwMemoryLoad",ctypes.c_ulong),
                      ("ullTotalPhys",ctypes.c_ulonglong),("ullAvailPhys",ctypes.c_ulonglong),
                      ("ullTotalPageFile",ctypes.c_ulonglong),("ullAvailPageFile",ctypes.c_ulonglong),
                      ("ullTotalVirtual",ctypes.c_ulonglong),("ullAvailVirtual",ctypes.c_ulonglong),
                      ("ullAvailExtendedVirtual",ctypes.c_ulonglong)]
        m=MEMORYSTATUSEX(); m.dwLength=ctypes.sizeof(m)
        if ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(m)):
            total=m.ullTotalPhys/(1024**3); avail=m.ullAvailPhys/(1024**3)
            used=max(total-avail,0); pct=(used/total*100) if total else 0
            info["memory"]=f"{total:.1f} GB"; info["memory_total_gb"]=round(total,1)
            info["memory_available_gb"]=round(avail,1); info["memory_used"]=f"{pct:.0f}% used"
    except Exception:
        pass

    # Disk
    try:
        root=Path.home().anchor or os.environ.get("SystemDrive","C:") + "\\"
        du=shutil.disk_usage(root); total=du.total/(1024**3); free=du.free/(1024**3)
        info["disk_total_gb"]=round(total,1); info["disk_free_gb"]=round(free,1)
        info["disk"]=f"{((total-free)/total*100) if total else 0:.0f}% used"
    except Exception:
        pass

    # Network adapters with PowerShell/CIM. This is read-only.
    try:
        ps_cmd=("Get-CimInstance Win32_NetworkAdapterConfiguration -Filter \"IPEnabled=TRUE\" "
                "| Select-Object Description,MACAddress,IPAddress,DefaultIPGateway,DNSServerSearchOrder "
                "| ConvertTo-Json -Compress")
        raw=_run_command(["powershell","-NoProfile","-Command",ps_cmd], timeout=8)
        if raw:
            data=json.loads(raw)
            if isinstance(data,dict): data=[data]
            records=[]
            for i,item in enumerate(data or []):
                ips=item.get("IPAddress") or []
                if isinstance(ips,str): ips=[ips]
                ipv4=[x for x in ips if "." in str(x)]
                ipv6=[x for x in ips if ":" in str(x)]
                records.append({
                    "Interface":item.get("Description") or f"Adapter {i+1}",
                    "Status":"UP",
                    "Speed":"OS-reported",
                    "IPv4":", ".join(map(str,ipv4)) or "—",
                    "IPv6":", ".join(map(str,ipv6)) or "—",
                    "MAC":item.get("MACAddress") or "—",
                    "Gateway":", ".join(map(str,item.get("DefaultIPGateway") or [])) or "—",
                    "DNS":", ".join(map(str,item.get("DNSServerSearchOrder") or [])) or "—",
                })
            info["interface_records"]=records
            info["interfaces"]=[r["Interface"] for r in records]
            info["interface_addresses"]=[f"{r['Interface']}: {r['IPv4']}" for r in records if r["IPv4"]!="—"]
    except Exception:
        pass

    # Netstat + tasklist mapping for listeners
    try:
        raw=_run_command(["netstat","-ano","-p","TCP"], timeout=6)
        listeners=[]
        for line in raw.splitlines():
            line=line.strip()
            if not line or line.lower().startswith("proto") or not line.upper().startswith("TCP"):
                continue
            parts=re.split(r"\s+",line)
            if len(parts)>=5 and parts[3].upper()=="LISTENING":
                local=parts[1]; pid=parts[4]
                port=local.rsplit(":",1)[-1]
                try: port_i=int(port)
                except Exception: continue
                proc_name="Unknown"
                if pid.isdigit():
                    for r in info.get("process_sample",[]):
                        if str(r.get("PID"))==pid:
                            proc_name=r.get("Process") or "Unknown"; break
                listeners.append({"Port":port_i,"Address":local.rsplit(":",1)[0],
                                  "PID":int(pid) if pid.isdigit() else pid,"Process":proc_name})
        # enrich process names for PIDs not in top-memory sample
        if listeners:
            try:
                rawp=_run_command(["tasklist","/fo","csv","/nh"], timeout=6)
                import csv, io
                pidmap={}
                for r in csv.reader(io.StringIO(rawp)):
                    if len(r)>=2: pidmap[str(r[1])]=r[0]
                for rec in listeners:
                    rec["Process"]=pidmap.get(str(rec["PID"]),rec["Process"])
            except Exception:
                pass
        info["listening_records"]=sorted(listeners,key=lambda x:x["Port"])[:50]
        info["listening_ports"]=sorted({x["Port"] for x in info["listening_records"]})
    except Exception:
        pass

    # Host addresses fallback
    if not info.get("interface_records"):
        try:
            ips=sorted({x[4][0] for x in socket.getaddrinfo(socket.gethostname(),None)
                        if x[0]==socket.AF_INET})
            if ips:
                info["interface_records"]=[{"Interface":"Host IPv4","Status":"UP","Speed":"OS lookup",
                                           "IPv4":", ".join(ips),"IPv6":"—",
                                           "MAC":":".join(f"{(uuid.getnode() >> (8*i)) & 0xff:02x}" for i in reversed(range(6))),
                                           "Gateway":"—","DNS":"OS resolver"}]
                info["interfaces"]=["Host IPv4"]
                info["interface_addresses"]=[f"Host IPv4: {', '.join(ips)}"]
        except Exception:
            pass

    return info


def local_host_evidence():
    """Collect non-invasive, read-only local host evidence.
    Prefer psutil; use a Windows-native fallback when psutil is unavailable.
    """
    info={
        "timestamp":datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "hostname":socket.gethostname(),
        "platform":platform.platform(),
        "os":f"{platform.system()} {platform.release()}",
        "python":platform.python_version(),
        "processor":platform.processor() or "Not reported by OS",
        "cpu_logical":None,"cpu_percent":None,"processes":None,"process_sample":[],
        "memory":None,"memory_used":None,"memory_total_gb":None,"memory_available_gb":None,
        "disk":None,"disk_total_gb":None,"disk_free_gb":None,
        "interfaces":[],"interface_records":[],"interface_addresses":[],
        "listening_ports":[],"listening_records":[],"uptime":None,"boot_time":None,
        "collector":"psutil" if psutil is not None else "Windows native fallback",
        "services_count":None,"running_services":None,"service_records":[],
        "certificate_count":None,"certificate_records":[],"firewall_records":[],
    }
    if psutil is None:
        info=_windows_fallback_evidence(info)
        return _collect_windows_extended_evidence(info)

    try: info["processes"]=len(psutil.pids())
    except Exception: pass
    try: info["cpu_logical"]=psutil.cpu_count(logical=True)
    except Exception: pass
    try: info["cpu_percent"]=psutil.cpu_percent(interval=0.35)
    except Exception: pass
    try:
        mem=psutil.virtual_memory()
        info["memory"]=f"{mem.total/(1024**3):.1f} GB"
        info["memory_used"]=f"{mem.percent:.0f}% used"
        info["memory_total_gb"]=round(mem.total/(1024**3),1)
        info["memory_available_gb"]=round(mem.available/(1024**3),1)
    except Exception: pass
    try:
        disk=psutil.disk_usage(Path.home().anchor or "/")
        info["disk"]=f"{disk.percent:.0f}% used"
        info["disk_total_gb"]=round(disk.total/(1024**3),1)
        info["disk_free_gb"]=round(disk.free/(1024**3),1)
    except Exception: pass
    try:
        boot=psutil.boot_time()
        info["boot_time"]=datetime.fromtimestamp(boot).strftime("%Y-%m-%d %H:%M:%S")
        info["uptime"]=str(timedelta(seconds=max(0,int(time.time()-boot))))
    except Exception: pass
    try:
        addrs=psutil.net_if_addrs(); stats=psutil.net_if_stats(); rows=[]
        for name,entries in addrs.items():
            ipv4=[]; ipv6=[]; mac=None
            for a in entries:
                fam=getattr(a,"family",None)
                if fam==socket.AF_INET: ipv4.append(a.address)
                elif fam==socket.AF_INET6: ipv6.append(a.address.split('%')[0])
                elif str(fam).endswith("AF_LINK") or str(fam).endswith("AF_PACKET"): mac=a.address
            stt=stats.get(name)
            rows.append({"Interface":name,"Status":"UP" if (stt and stt.isup) else "DOWN/UNKNOWN",
                         "Speed":f"{stt.speed} Mbps" if (stt and stt.speed and stt.speed>0) else "N/A",
                         "IPv4":", ".join(ipv4) or "—","IPv6":", ".join(ipv6) or "—",
                         "MAC":mac or "—","Gateway":"—","DNS":"OS-resolved"})
            for ip in ipv4: info["interface_addresses"].append(f"{name}: {ip}")
        info["interface_records"]=rows; info["interfaces"]=sorted(addrs.keys())
    except Exception: pass
    try:
        conns=psutil.net_connections(kind="inet"); records=[]
        for c in conns:
            if c.status!=psutil.CONN_LISTEN or not c.laddr: continue
            pid=getattr(c,"pid",None); proc_name="Unknown"
            if pid:
                try: proc_name=psutil.Process(pid).name()
                except Exception: pass
            records.append({"Port":c.laddr.port,"Address":c.laddr.ip,"PID":pid or "—","Process":proc_name})
        info["listening_records"]=sorted(records,key=lambda x:(int(x["Port"]),str(x["Process"])))[:50]
        info["listening_ports"]=sorted({x["Port"] for x in info["listening_records"]})
    except Exception: pass
    try:
        sample=[]
        for proc in psutil.process_iter(["pid","name","status","memory_info","username","create_time"]):
            try:
                mi=proc.info.get("memory_info")
                sample.append({"PID":proc.info.get("pid"),"Process":proc.info.get("name") or "Unknown",
                               "Status":proc.info.get("status") or "—",
                               "Memory MB":round((mi.rss if mi else 0)/(1024**2),1),
                               "User":proc.info.get("username") or "—",
                               "Started":datetime.fromtimestamp(proc.info.get("create_time")).strftime("%H:%M:%S") if proc.info.get("create_time") else "—"})
            except Exception: continue
        info["process_sample"]=sorted(sample,key=lambda x:float(x.get("Memory MB") or 0),reverse=True)[:20]
    except Exception: pass
    return _collect_windows_extended_evidence(info)


def runtime_graph_figure(ev):
    """Visualize only host observations that map to NEXORA discovery layers."""
    nodes=[]; edges=[]
    def add(n,label,kind):
        if n not in [x[0] for x in nodes]:
            nodes.append((n,label,kind))
    add("HOST",ev.get("hostname") or "Execution host","host")
    add("OS",ev.get("os") or "Operating system","os"); edges.append(("HOST","OS"))
    add("RUNTIME",f"Python {ev.get('python','N/A')}","runtime"); edges.append(("HOST","RUNTIME"))

    if ev.get("process_sample"):
        add("PROCESSES",f"{len(ev.get('process_sample') or [])} observed","process")
        edges.append(("HOST","PROCESSES"))
    if ev.get("service_records"):
        add("SERVICES",f"{ev.get('running_services','?')} running","service")
        edges.append(("HOST","SERVICES"))
    if ev.get("interface_records"):
        add("NETWORK",f"{len(ev.get('interface_records') or [])} interface(s)","network")
        edges.append(("HOST","NETWORK"))
    if ev.get("listening_records"):
        add("LISTENERS",f"{len(ev.get('listening_records') or [])} TCP","listener")
        edges.append(("NETWORK","LISTENERS"))
    if ev.get("certificate_records"):
        add("CERTS",f"{len(ev.get('certificate_records') or [])} cert(s)","crypto")
        edges.append(("HOST","CERTS"))
    crypto_count=len(ev.get("crypto_implementations") or [])+len(ev.get("python_crypto_packages") or [])
    if crypto_count:
        add("CRYPTO",f"{crypto_count} implementation(s)","crypto")
        edges.append(("RUNTIME","CRYPTO"))

    import math
    pos={"HOST":(0,0),"OS":(-3,2.3),"RUNTIME":(3,2.3)}
    others=[n for n,_,_ in nodes if n not in pos]
    for j,n in enumerate(others):
        a=2*math.pi*j/max(1,len(others))
        pos[n]=(4.4*math.cos(a),4.4*math.sin(a))

    fig=go.Figure()
    for a,b in edges:
        if a not in pos or b not in pos: continue
        fig.add_trace(go.Scatter(
            x=[pos[a][0],pos[b][0]],y=[pos[a][1],pos[b][1]],
            mode="lines",line=dict(color="#31536c",width=1.8),
            hoverinfo="skip",showlegend=False))
    groups={"host":[],"os":[],"runtime":[],"process":[],"service":[],"network":[],"listener":[],"crypto":[]}
    for n,label,kind in nodes:
        groups.setdefault(kind,[]).append((n,label))
    names={"host":"HOST","os":"OS","runtime":"NEXORA RUNTIME","process":"PROCESSES",
           "service":"SERVICES","network":"NETWORK","listener":"LISTENERS","crypto":"CRYPTO"}
    sizes={"host":38,"os":31,"runtime":31,"process":25,"service":25,"network":28,"listener":24,"crypto":30}
    for kind,items in groups.items():
        if not items: continue
        fig.add_trace(go.Scatter(
            x=[pos[n][0] for n,_ in items],y=[pos[n][1] for n,_ in items],
            mode="markers+text",text=[label for _,label in items],
            textposition="middle center",
            marker=dict(size=sizes.get(kind,24),line=dict(width=1,color="#6eb8ea")),
            name=names.get(kind,kind.upper()),
            hovertemplate="%{text}<extra></extra>"))
    fig.update_layout(
        height=500,margin=dict(l=20,r=20,t=15,b=55),
        paper_bgcolor="#0b1219",plot_bgcolor="#0b1219",
        font=dict(color="#dce8f1"),showlegend=True,
        legend=dict(orientation="h",y=-0.06,x=0),
        xaxis=dict(visible=False),yaxis=dict(visible=False),hovermode="closest")
    return fig

def runtime_resource_figure(ev):
    labels=["CPU load","Memory used","Disk used"]
    vals=[float(ev.get("cpu_percent") or 0),
          float(str(ev.get("memory_used") or "0").replace("% used","") or 0),
          float(str(ev.get("disk") or "0").replace("% used","") or 0)]
    fig=go.Figure(go.Bar(x=vals,y=labels,orientation="h",
                         text=[f"{v:.0f}%" for v in vals],textposition="auto",
                         marker=dict(color=["#67b7e8","#74d7a2","#f0b56b"])))
    fig.update_layout(height=240,margin=dict(l=10,r=15,t=15,b=20),paper_bgcolor="#0b1219",
                      plot_bgcolor="#0b1219",xaxis=dict(range=[0,100],title="Utilization (%)"),
                      yaxis=dict(title=""),font=dict(color="#dce8f1"),showlegend=False)
    return fig

def process_memory_figure(ev):
    rows=ev.get("process_sample") or []
    if not rows: return None
    d=pd.DataFrame(rows).head(10).sort_values("Memory MB")
    fig=go.Figure(go.Bar(x=d["Memory MB"],y=d["Process"],orientation="h",
                         text=[f"{x:.1f} MB" for x in d["Memory MB"]],textposition="auto",
                         marker=dict(color="#6eb8ea")))
    fig.update_layout(height=330,margin=dict(l=10,r=20,t=15,b=20),paper_bgcolor="#0b1219",
                      plot_bgcolor="#0b1219",xaxis_title="Resident memory (MB)",
                      yaxis_title="",font=dict(color="#dce8f1"),showlegend=False)
    return fig


def cmis_breakdown(row):
    dependency_factor=min(max(len(impacted_components(row["id"]))-1,0),5)
    vulnerability=ALGORITHM_VULNERABILITY.get(row["algorithm"],2)
    parts=[
        ("Cryptographic vulnerability",vulnerability,8,vulnerability*8),
        ("Criticality",int(row["criticality"]),6,int(row["criticality"])*6),
        ("Exposure",int(row["exposure"]),5,int(row["exposure"])*5),
        ("Migration complexity",int(row["complexity"]),4,int(row["complexity"])*4),
        ("Dependency impact factor",dependency_factor,3,dependency_factor*3),
    ]
    raw=sum(x[3] for x in parts)
    return parts,raw,min(round(raw),100)

def assessment_radar_figure(row):
    labels=["Vulnerability","Criticality","Exposure","Complexity","Dependency depth"]
    vals=[
        ALGORITHM_VULNERABILITY.get(row["algorithm"],2),
        int(row["criticality"]),int(row["exposure"]),int(row["complexity"]),
        min(max(max(dependency_depths(row.id).values(),default=0),0),5)
    ]
    vals=vals+[vals[0]]
    labels=labels+[labels[0]]
    fig=go.Figure(go.Scatterpolar(r=vals,theta=labels,fill="toself",
                                  line=dict(color="#6eb8ea",width=3),
                                  fillcolor="rgba(110,184,234,.18)",
                                  name=str(row["name"])))
    fig.update_layout(height=360,margin=dict(l=45,r=45,t=35,b=35),
                      paper_bgcolor="#0b1219",plot_bgcolor="#0b1219",
                      polar=dict(radialaxis=dict(range=[0,5],dtick=1,
                                                 gridcolor="#294050",color="#9db0bf"),
                                 angularaxis=dict(gridcolor="#294050",color="#dbe8ef")),
                      font=dict(color="#dce8f1"),showlegend=False)
    return fig

def assessment_landscape_figure(selected):
    d=df.copy()
    d["Impact"]=d["Impacted Components"]
    d["Effort rank"]=d["ML Effort"].map({"LOW":1,"MODERATE":2,"HIGH":3,"CRITICAL":4}).fillna(1)
    fig=go.Figure()
    risk_order=["LOW","MODERATE","HIGH","CRITICAL"]
    risk_colors={"LOW":"#74d7a2","MODERATE":"#f0b56b","HIGH":"#e9a66b","CRITICAL":"#f07f7f"}
    for risk in risk_order:
        q=d[d["Risk"]==risk]
        if q.empty: continue
        fig.add_trace(go.Scatter(x=q["Impact"],y=q["CMIS"],mode="markers",
                                 marker=dict(size=12,color=risk_colors[risk],line=dict(width=1,color="#dce8f1")),
                                 text=q["name"],customdata=q["id"],
                                 hovertemplate="<b>%{text}</b><br>Impact: %{x}<br>CMIS: %{y}<br>Risk: "+risk+"<extra></extra>",
                                 name=risk))
    s=d[d.id==selected]
    if not s.empty:
        fig.add_trace(go.Scatter(x=s["Impact"],y=s["CMIS"],mode="markers+text",
                                 marker=dict(size=22,color="#ffffff",symbol="star",line=dict(width=2,color="#6eb8ea")),
                                 text=["SELECTED"],textposition="top center",
                                 hovertemplate="<b>Selected asset</b><br>Impact: %{x}<br>CMIS: %{y}<extra></extra>",
                                 name="Selected"))
    fig.update_layout(height=360,margin=dict(l=20,r=15,t=15,b=35),
                      paper_bgcolor="#0b1219",plot_bgcolor="#0b1219",
                      xaxis=dict(title="Affected modeled components",gridcolor="#243947",dtick=1),
                      yaxis=dict(title="CMIS (NEXORA project metric)",range=[0,105],gridcolor="#243947"),
                      font=dict(color="#dce8f1"),legend=dict(orientation="h",y=1.08,x=0))
    return fig

def assessment_feature_figure():
    imp=pd.Series(MODEL.feature_importances_,index=ML_FEATURES).sort_values()
    names={
        "criticality":"Criticality","exposure":"Exposure","complexity":"Complexity",
        "dependency_depth":"Dependency depth","operational_dependents":"Operational dependents",
        "technical_dependencies":"Technical dependencies","vulnerability":"Crypto vulnerability"
    }
    labels=[names.get(x,x) for x in imp.index]
    fig=go.Figure(go.Bar(x=imp.values,y=labels,orientation="h",
                         text=[f"{v:.1%}" for v in imp.values],textposition="auto",
                         marker=dict(color="#6eb8ea")))
    fig.update_layout(height=330,margin=dict(l=15,r=25,t=15,b=25),
                      paper_bgcolor="#0b1219",plot_bgcolor="#0b1219",
                      xaxis=dict(title="Relative feature contribution",tickformat=".0%"),
                      yaxis=dict(title=""),font=dict(color="#dce8f1"),showlegend=False)
    return fig

def exposure_summary():
    critical = int((df["Risk"] == "CRITICAL").sum())
    high = int((df["Risk"] == "HIGH").sum())
    moderate = int((df["Risk"] == "MODERATE").sum())
    if critical:
        return "CRITICAL EXPOSURE", "At least one modeled asset is in the critical band."
    if high:
        return "HIGH EXPOSURE", "Classical cryptographic assets have modeled migration consequences."
    if moderate:
        return "MODERATE EXPOSURE", "Migration planning is required for the modeled classical assets."
    return "LOW EXPOSURE", "No high/critical modeled asset was detected in this case."

def next_stage(stage):
    order=["CASE","DISCOVER","TRACE","DECIDE","SIMULATE","CONCLUDE"]
    try:
        i=order.index(stage)
        return order[min(i+1,len(order)-1)]
    except ValueError:
        return "CASE"

# ============================================================

# ============================================================
# NEXORA V13 — FINAL EVIDENCE-DRIVEN EXPERIENCE
# ============================================================

import html

st.markdown("""
<style>
:root{
 --nx-bg:#070a0f;--nx-panel:#101720;--nx-panel2:#131d28;--nx-line:#29394a;
 --nx-text:#f2f6fa;--nx-muted:#91a0b1;--nx-blue:#70b9ff;--nx-green:#64d29b;
 --nx-amber:#e6bd68;--nx-red:#ef747d;--nx-red2:#5d2e36;
}
html,body,[data-testid="stAppViewContainer"]{background:var(--nx-bg);color:var(--nx-text)}
[data-testid="stHeader"]{display:flex!important;background:transparent!important;border-bottom:0!important;box-shadow:none!important}
[data-testid="stToolbar"]{display:none!important}
.block-container{max-width:1460px;padding-top:1.35rem!important;padding-bottom:4rem!important}
[data-testid="stSidebar"]{background:#0c1118;border-right:1px solid #1d2936}
h1,h2,h3{letter-spacing:-.025em}
.nx-page{animation:nxIn .32s ease-out both}@keyframes nxIn{from{opacity:0;transform:translateY(6px)}to{opacity:1;transform:none}}
@keyframes nxPulse{0%,100%{opacity:.45;transform:scale(.92)}50%{opacity:1;transform:scale(1)}}
@keyframes nxSweep{0%{background-position:120% 0}100%{background-position:-20% 0}}
.nx-brand-row{display:flex;justify-content:space-between;align-items:center;gap:18px;margin:2px 0 10px}
.nx-brand{font-size:2.55rem;font-weight:900;letter-spacing:-.065em;line-height:1}
.nx-sub{color:#91a4b8;font-size:.93rem;margin-top:.34rem}
.nx-live{display:inline-flex;align-items:center;gap:8px;padding:7px 11px;border-radius:999px;border:1px solid #294238;background:#0d1915;color:#a5e4c1;font-size:.68rem;font-weight:850;letter-spacing:.065em;text-transform:uppercase}
.nx-dot{width:7px;height:7px;border-radius:50%;background:#64d29b;animation:nxPulse 1.8s ease-in-out infinite}
.nx-case-strip{display:flex;align-items:center;justify-content:space-between;gap:14px;flex-wrap:wrap;background:#0d141c;border:1px solid #263544;border-radius:13px;padding:10px 13px;margin:10px 0 11px}
.nx-case-strip-main{font-weight:800}.nx-case-strip-id{color:#77879a;font-size:.76rem;margin-left:7px}.nx-case-strip-meta{display:flex;gap:7px;flex-wrap:wrap}
.nx-chip{padding:5px 8px;border:1px solid #2c3b4c;border-radius:999px;color:#aab8c7;font-size:.67rem;letter-spacing:.035em}
.nx-chip.good{border-color:#315b49;color:#a8e6c6}.nx-chip.danger{border-color:#623b42;color:#f3a0a6;background:#181014}
.nx-progress-wrap{padding:3px 0 9px;margin-bottom:18px;background:var(--nx-bg)}
.nx-progress{display:flex;align-items:center;gap:5px;flex-wrap:wrap}
.nx-progress-item{padding:8px 11px;border:1px solid #293747;background:#101720;border-radius:9px;color:#8796a8;font-size:.72rem;transition:.18s}
.nx-progress-item.active{border-color:#5d9fe0;background:#14263a;color:#eff7ff;box-shadow:0 0 0 1px rgba(93,159,224,.12)}
.nx-progress-item.done{color:#c5d2df;background:#0f1821}
.nx-progress-arrow{color:#4f6174}.nx-progress-meta{display:flex;justify-content:space-between;color:#718092;font-size:.67rem;margin:5px 2px}
.nx-line{height:2px;background:#1d2936;border-radius:9px;overflow:hidden}.nx-fill{height:100%;background:linear-gradient(90deg,#4f91d5,#79bcff);transition:width .45s}
.nx-enginebar{display:flex;align-items:center;gap:9px;flex-wrap:wrap;margin:0 0 18px}
.nx-engine-state{padding:7px 10px;border:1px solid #315542;background:#0d1915;border-radius:9px;color:#a8e5c4;font-size:.72rem;font-weight:800}
.nx-engine-detail{color:#78899b;font-size:.72rem}
.nx-hero{position:relative;overflow:hidden;background:linear-gradient(135deg,#13202c,#0c131b);border:1px solid #2e4052;border-radius:23px;padding:43px 44px;margin:14px 0 30px;box-shadow:0 20px 70px rgba(0,0,0,.24)}
.nx-hero:after{content:"";position:absolute;inset:0;background:linear-gradient(110deg,transparent 30%,rgba(107,176,255,.06) 48%,transparent 66%);background-size:220% 100%;animation:nxSweep 10s linear infinite;pointer-events:none}
.nx-hero>*{position:relative;z-index:1}.nx-eyebrow{color:#78baff;font-size:.69rem;font-weight:900;letter-spacing:.14em;text-transform:uppercase}
.nx-hero h1{font-size:2.55rem;line-height:1.08;margin:.55rem 0 .85rem;max-width:1100px}.nx-hero p{color:#aab9c8;font-size:1.03rem;line-height:1.72;max-width:1080px}
.nx-section{margin-top:34px}.nx-section-title{font-size:1.48rem;font-weight:850;margin-bottom:.35rem}.nx-section-sub{color:#8f9dac;line-height:1.55;margin-bottom:16px}
.nx-case-card{background:linear-gradient(180deg,#111b25,#0d141c);border:1px solid #2b3a4a;border-radius:19px;padding:22px;height:100%;position:relative;overflow:hidden;transition:.2s}
.nx-case-card:hover{transform:translateY(-4px);border-color:#4c7199;box-shadow:0 18px 40px rgba(0,0,0,.24)}
.nx-case-card.featured{border-color:#3d6184}.nx-case-icon{font-size:2.05rem}.nx-case-title{font-size:1.28rem;font-weight:850;margin:8px 0}
.nx-case-desc{color:#a9b7c6;line-height:1.55;min-height:76px}.nx-case-why{background:#0a1118;border:1px solid #263543;border-radius:12px;padding:13px;margin:15px 0;line-height:1.55}
.nx-metrics{display:grid;grid-template-columns:repeat(3,1fr);gap:7px;margin:14px 0}.nx-metric{background:#0a1118;border:1px solid #24313f;border-radius:10px;padding:9px}.nx-metric b{display:block;font-size:1.05rem}.nx-metric span{font-size:.64rem;color:#7f8c9c;text-transform:uppercase;letter-spacing:.05em}
.nx-preview{display:flex;align-items:center;justify-content:space-between;gap:10px;padding:10px 11px;background:#0a1118;border:1px solid #273645;border-radius:10px;margin-top:10px}
.nx-preview .label{color:#7f90a2;font-size:.63rem;text-transform:uppercase;letter-spacing:.08em}.nx-preview .value{font-weight:800;font-size:.84rem}
.nx-card{background:linear-gradient(180deg,#101821,#0e151d);border:1px solid #293646;border-radius:15px;padding:18px;transition:.18s;box-shadow:0 7px 24px rgba(0,0,0,.08)}
.nx-card:hover{border-color:#3d5268}.nx-card h3{margin:.25rem 0 .45rem}.nx-card p{line-height:1.55}.nx-card-danger{border-color:#684149;background:#191316}.nx-card-ok{border-color:#345847;background:#101b17}
.nx-brief{background:linear-gradient(135deg,#121d28,#0d141c);border:1px solid #2d3d4d;border-radius:20px;padding:27px;margin:15px 0 20px;box-shadow:0 12px 38px rgba(0,0,0,.14)}
.nx-brief h1{font-size:2rem;margin:.35rem 0}.nx-brief p{color:#aab6c4;line-height:1.65}.nx-badge{display:inline-block;padding:6px 10px;border:1px solid #344356;border-radius:999px;color:#b8c5d4;font-size:.7rem;margin:3px 5px 3px 0}
.nx-kpi{background:linear-gradient(180deg,#101821,#0e151d);border:1px solid #293646;border-radius:14px;padding:15px;min-height:88px;transition:.18s}.nx-kpi:hover{transform:translateY(-2px);border-color:#3b4d60}
.nx-kpi-label{color:#8291a2;font-size:.67rem;text-transform:uppercase;letter-spacing:.07em}.nx-kpi-value{font-size:1.42rem;font-weight:850;margin-top:5px}.nx-kpi-danger{border-color:#654047;background:#191317}
.nx-finding{background:#121a24;border:1px solid #37516d;border-left:4px solid var(--nx-blue);border-radius:15px;padding:19px 20px}.nx-finding.critical{border-color:#684149;border-left-color:var(--nx-red);background:#191316}
.nx-finding-title{font-size:.7rem;font-weight:900;letter-spacing:.11em;color:#83bcf7;text-transform:uppercase}.nx-finding h2{margin:.4rem 0 .5rem;font-size:1.38rem}.nx-finding p{color:#b2bdca;line-height:1.6;margin:0}
.nx-warning{background:#17151a;border:1px solid #4e4146;border-left:4px solid var(--nx-amber);border-radius:13px;padding:16px 18px;line-height:1.58}.nx-warning-title{font-weight:850;color:#f0dfb8}
.nx-decision{background:linear-gradient(135deg,#121d2a,#101822);border:1px solid #365b7f;border-radius:17px;padding:22px;box-shadow:0 12px 32px rgba(0,0,0,.13)}.nx-decision h2{font-size:1.8rem;margin:.35rem 0}.nx-decision p{color:#aebaca;line-height:1.6}
.nx-evidence{background:#0d141c;border:1px dashed #344354;border-radius:13px;padding:15px;line-height:1.65}.nx-chain{background:#0c1219;border:1px solid #293646;border-radius:13px;padding:14px 16px;font-family:ui-monospace,SFMono-Regular,Menlo,monospace;line-height:1.8;margin:7px 0;transition:.18s}.nx-chain:hover{border-color:#456077}
.nx-legend{background:#0d141c;border:1px solid #273442;border-radius:11px;padding:10px 13px;color:#9eabb9;font-size:.76rem;margin:10px 0 14px;line-height:1.7}
.nx-grid-step{background:linear-gradient(180deg,#101821,#0e151d);border:1px solid #2a3746;border-radius:14px;padding:17px;min-height:125px;transition:.18s}.nx-grid-step:hover{transform:translateY(-2px);border-color:#3d5369}
.nx-step-num{color:#73b5ff;font-size:.7rem;font-weight:900;letter-spacing:.07em}.nx-grid-step h3{font-size:1rem;margin:.45rem 0}.nx-grid-step p{color:#8f9dac;font-size:.8rem;line-height:1.5}
.nx-roadmap{display:flex;align-items:stretch;gap:0;margin:14px 0 20px;overflow-x:auto;padding:5px 0 12px}
.nx-road-node{min-width:205px;background:#101821;border:1px solid #2b3948;border-radius:14px;padding:16px;position:relative}.nx-road-node.active{border-color:#4c83b6;background:#12202d;box-shadow:0 0 0 1px rgba(76,131,182,.1)}
.nx-road-node .n{color:#73b5ff;font-size:.68rem;font-weight:900}.nx-road-node h3{font-size:.9rem;margin:.35rem 0}.nx-road-node p{color:#8f9cab;font-size:.75rem;line-height:1.45}.nx-road-arrow{display:flex;align-items:center;padding:0 9px;color:#607287;font-size:1.2rem}
.nx-verdict{background:#0f1b16;border:1px solid #315846;border-radius:16px;padding:21px;box-shadow:0 10px 28px rgba(0,0,0,.12)}.nx-verdict h2{color:#bff1d6;margin:.3rem 0}.nx-footer{color:#687789;font-size:.75rem;border-top:1px solid #202b38;margin-top:32px;padding-top:18px;line-height:1.55}
.nx-table-note{color:#8391a1;font-size:.77rem;margin:5px 0 10px}.nx-question{font-size:1.72rem;font-weight:850;margin-top:4px}.nx-question-sub{color:#98a5b4;margin:5px 0 18px;line-height:1.55}
.nx-plain{font-size:.95rem;line-height:1.7;color:#b4c0cc}.nx-callout{padding:14px 16px;border-radius:12px;background:#0d141c;border:1px solid #283746;line-height:1.6}.nx-small{font-size:.75rem;color:#7f8d9d}.nx-success{color:#a7e6c5}.nx-critical-text{color:#f29aa0}.nx-amber-text{color:#e7c475}
.nx-activity{background:#0a1118;border:1px solid #243342;border-radius:13px;padding:13px}.nx-activity-row{display:flex;gap:10px;align-items:flex-start;padding:7px 0;border-bottom:1px solid #1b2632;font-size:.77rem}.nx-activity-row:last-child{border-bottom:0}.nx-activity-dot{width:7px;height:7px;border-radius:50%;background:#69b6ff;margin-top:5px;flex:0 0 auto}.nx-activity-time{color:#607184;font-family:ui-monospace,monospace;font-size:.66rem;min-width:52px}.nx-activity-text{color:#a9b6c5}
.nx-architecture{display:flex;align-items:center;gap:7px;overflow-x:auto;padding:4px 0 10px}.nx-arch-node{min-width:125px;padding:12px 13px;border:1px solid #2b3b4c;border-radius:11px;background:#0e161f;text-align:center}.nx-arch-node b{display:block;font-size:.76rem}.nx-arch-node span{color:#718397;font-size:.62rem}.nx-arch-arrow{color:#4d6075}
.nx-meter{height:7px;background:#1c2733;border-radius:99px;overflow:hidden;margin-top:7px}.nx-meter>span{display:block;height:100%;background:linear-gradient(90deg,#5d9fe0,#79c5ff);border-radius:99px}
.nx-exposure-panel{border:1px solid #4b3037;background:linear-gradient(135deg,#171014,#10151b);border-radius:17px;padding:20px}
.nx-exposure-panel .big{font-size:2.2rem;font-weight:900;letter-spacing:-.04em}.nx-exposure-panel .sub{color:#9eabb8;line-height:1.55}
.nx-side-title{color:#8292a4;font-size:.67rem;font-weight:900;letter-spacing:.11em;text-transform:uppercase;margin-bottom:8px}
.stButton>button{border-radius:10px!important;transition:.16s!important}.stButton>button:hover{transform:translateY(-1px)!important;box-shadow:0 7px 20px rgba(0,0,0,.16)!important}
[data-testid="stSidebar"] .stRadio label{transition:.15s}.stSelectbox>div>div{border-radius:10px}
@media(max-width:900px){.nx-brand-row{align-items:flex-start}.nx-hero{padding:30px 24px}.nx-hero h1{font-size:1.9rem}.nx-metrics{grid-template-columns:1fr 1fr}.nx-roadmap{overflow-x:auto}.nx-case-strip-meta{width:100%}}

.v19-hero{position:relative;overflow:hidden;border:1px solid #2b4256;border-radius:24px;padding:38px 42px;margin:18px 0 24px;background:linear-gradient(135deg,#0c151e 0%,#0b1118 58%,#101b27 100%);box-shadow:0 22px 65px rgba(0,0,0,.25)}
.v19-hero:before{content:"";position:absolute;width:420px;height:420px;right:-130px;top:-170px;border:1px solid rgba(112,185,255,.14);border-radius:50%;box-shadow:0 0 0 45px rgba(112,185,255,.025),0 0 0 90px rgba(112,185,255,.018)}
.v19-hero h1{position:relative;font-size:2.7rem;line-height:1.05;max-width:950px;margin:8px 0 13px;letter-spacing:-.045em}.v19-hero p{position:relative;max-width:900px;color:#a8b8c7;font-size:1rem;line-height:1.65;margin:0}
.v19-answer{position:relative;margin-top:25px;padding-top:18px;border-top:1px solid #263848;max-width:820px}.v19-answer span{display:block;color:#6fb7f3;font-size:.63rem;font-weight:900;letter-spacing:.14em;text-transform:uppercase}.v19-answer b{display:block;font-size:1.05rem;margin-top:5px}
.v19-flow{display:flex;align-items:center;gap:8px;flex-wrap:wrap;margin-top:25px}.v19-flow-step{border:1px solid #30485c;background:#0c1721;padding:8px 12px;border-radius:8px;color:#a9d2f2;font-size:.67rem;font-weight:900;letter-spacing:.09em}.v19-flow-arrow{color:#526d82}
.v19-case-file{border:1px solid #293b4d;border-radius:15px;background:#0d151e;padding:18px 18px 15px;height:100%;transition:.18s}.v19-case-file:hover{border-color:#4d78a0;transform:translateY(-2px)}
.v19-case-top{display:flex;justify-content:space-between;align-items:center;gap:10px}.v19-case-icon{font-size:1.25rem}.v19-case-id{color:#6388a8;font-size:.67rem;font-weight:900;letter-spacing:.1em}.v19-case-file h3{font-size:1.05rem;margin:13px 0 7px}.v19-case-file p{color:#9caebe;font-size:.82rem;line-height:1.55;min-height:52px}.v19-case-path{display:flex;gap:5px;align-items:center;flex-wrap:wrap;margin:13px 0}.v19-path-chip{padding:5px 7px;border:1px solid #2c4053;border-radius:6px;color:#a8c4d9;font-size:.62rem}.v19-path-arrow{color:#526b7d;font-size:.7rem}.v19-case-finding{border-top:1px solid #243441;padding-top:11px;margin-top:10px}.v19-case-finding span{display:block;color:#6f879c;font-size:.58rem;font-weight:900;letter-spacing:.1em}.v19-case-finding b{display:block;font-size:.78rem;margin-top:4px}.v19-case-file button{margin-top:12px}
.v19-section-label{font-size:.68rem;font-weight:900;letter-spacing:.13em;color:#6faedb;text-transform:uppercase;margin:26px 0 9px}.v19-section-copy{color:#8fa0b0;font-size:.82rem;margin-bottom:12px}
.v19-investigation{display:grid;grid-template-columns:repeat(6,1fr);gap:0;border:1px solid #263848;border-radius:13px;overflow:hidden;background:#0c131b;margin:17px 0 24px}.v19-investigation-step{padding:15px 13px;border-right:1px solid #253542;position:relative}.v19-investigation-step:last-child{border-right:0}.v19-investigation-step .n{color:#5f92ba;font-size:.6rem;font-weight:900}.v19-investigation-step b{display:block;font-size:.78rem;margin-top:6px}.v19-investigation-step span{display:block;color:#718496;font-size:.67rem;line-height:1.4;margin-top:5px}@media(max-width:900px){.v19-investigation{grid-template-columns:1fr 1fr}.v19-investigation-step{border-bottom:1px solid #253542}.v19-hero{padding:28px 24px}.v19-hero h1{font-size:2.15rem}}
.v19-source{border-top:1px solid #263848;border-bottom:1px solid #263848;padding:17px 0;margin:23px 0;color:#94a8b9}.v19-source b{color:#e4edf5}.v19-source a{color:#75b8ef;text-decoration:none;margin-right:18px;font-size:.72rem}.v19-source a:hover{text-decoration:underline}
.v19-finding{border-left:3px solid #5ca7df;padding:3px 0 3px 16px;margin:16px 0 21px}.v19-finding span{display:block;color:#6eaee0;font-size:.61rem;font-weight:900;letter-spacing:.12em}.v19-finding h2{font-size:1.28rem;margin:5px 0 4px}.v19-finding p{color:#94a5b5;margin:0;font-size:.84rem;line-height:1.55}
.v19-focus{display:flex;align-items:center;gap:0;border:1px solid #2a3d4f;border-radius:12px;background:#0c141d;margin:13px 0 20px;overflow:hidden}.v19-focus-main{padding:13px 16px;flex:1}.v19-focus-main span,.v19-focus-stat span{display:block;color:#63819b;font-size:.58rem;font-weight:900;letter-spacing:.1em}.v19-focus-main b{display:block;font-size:.93rem;margin-top:4px}.v19-focus-stat{min-width:125px;padding:13px 15px;border-left:1px solid #263848}.v19-focus-stat b{display:block;font-size:.9rem;margin-top:4px;color:#dce8f2}@media(max-width:900px){.v19-focus{flex-wrap:wrap}.v19-focus-stat{flex:1;border-left:0;border-top:1px solid #263848}}
.v19-readout{height:100%;border-left:2px solid #31536d;padding:3px 0 3px 18px}.v19-readout .eyebrow{color:#6eb6ed;font-size:.61rem;font-weight:900;letter-spacing:.12em}.v19-readout h3{margin:6px 0 8px;font-size:1.1rem}.v19-readout p{color:#97a9b9;font-size:.8rem;line-height:1.6;margin:0 0 11px}.v19-readout ul{padding-left:17px;margin:8px 0}.v19-readout li{color:#a7b5c2;font-size:.78rem;line-height:1.65}.v19-readout .lead{font-size:.96rem;color:#e3edf5;font-weight:750}
.v19-table-caption{display:flex;justify-content:space-between;align-items:end;gap:15px;margin:22px 0 8px}.v19-table-caption h3{margin:0;font-size:1.05rem}.v19-table-caption p{margin:3px 0 0;color:#718596;font-size:.72rem}.v19-table-note{color:#64829b;font-size:.62rem;font-weight:800;letter-spacing:.08em;text-transform:uppercase}
.v19-runtime{border-top:1px solid #273949;margin-top:27px;padding-top:21px}.v19-runtime-head{display:flex;justify-content:space-between;align-items:end;gap:15px}.v19-runtime-head h3{margin:4px 0;font-size:1.15rem}.v19-runtime-head p{margin:0;color:#8395a7;font-size:.77rem;line-height:1.5;max-width:750px}.v19-runtime-grid{display:grid;grid-template-columns:1.5fr 1fr 1fr 1fr;gap:0;border:1px solid #293b4b;border-radius:12px;overflow:hidden;margin-top:14px;background:#0b1219}.v19-runtime-cell{padding:14px 15px;border-right:1px solid #243543}.v19-runtime-cell:last-child{border-right:0}.v19-runtime-cell span{display:block;color:#63819a;font-size:.57rem;font-weight:900;letter-spacing:.1em}.v19-runtime-cell b{display:block;color:#e0e9f0;font-size:.84rem;margin-top:5px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}@media(max-width:900px){.v19-runtime-grid{grid-template-columns:1fr 1fr}.v19-runtime-cell:nth-child(2){border-right:0}.v19-runtime-cell:nth-child(3),.v19-runtime-cell:nth-child(4){border-top:1px solid #243543}}
.v19-runtime-detail{color:#8194a5;font-size:.72rem;line-height:1.65;padding-top:9px}.v19-runtime-detail b{color:#b9c9d6}
.v19-graph-shell{border:1px solid #273949;border-radius:15px;background:#0b1219;overflow:hidden}.v19-graph-head{padding:13px 16px;border-bottom:1px solid #243543;display:flex;justify-content:space-between;gap:15px;align-items:center}.v19-graph-head span{color:#63829b;font-size:.61rem;font-weight:900;letter-spacing:.1em}.v19-graph-head b{font-size:.82rem}.v19-graph-reading{padding:14px 16px;border-top:1px solid #253744;color:#91a4b5;font-size:.76rem;line-height:1.55}.v19-legend{display:flex;gap:10px;flex-wrap:wrap;margin-top:8px}.v19-legend span{color:#8fa2b3;font-size:.62rem}.v19-legend b{color:#dbe6ee}.v19-path-line{display:flex;align-items:center;gap:7px;flex-wrap:wrap;margin:13px 0}.v19-path-node{padding:6px 8px;border:1px solid #2d4254;border-radius:7px;background:#0e1821;color:#c2d0db;font-size:.65rem}.v19-path-node.focus{border-color:#5fa8df;color:#e4f2ff}.v19-path-arrow{color:#557087}
.v19-evidence-table{border-top:1px solid #263848;border-bottom:1px solid #263848;margin-top:20px}.v19-evidence-line{display:grid;grid-template-columns:160px 1fr;border-bottom:1px solid #202f3d;padding:12px 0}.v19-evidence-line:last-child{border-bottom:0}.v19-evidence-line span{color:#62829d;font-size:.62rem;font-weight:900;letter-spacing:.1em}.v19-evidence-line b{font-size:.79rem;color:#d9e5ed;font-weight:650}.v19-evidence-line p{margin:2px 0 0;color:#8295a7;font-size:.72rem;line-height:1.5}
.v19-assess-grid{display:grid;grid-template-columns:1.1fr .9fr;gap:25px;margin-top:17px}.v19-assess-block{border-top:1px solid #293b4b;padding-top:14px}.v19-assess-block h3{margin:0 0 9px;font-size:1rem}.v19-assess-block p{color:#8ea1b2;font-size:.78rem;line-height:1.6}.v19-gauge{height:8px;background:#18232e;border-radius:99px;overflow:hidden;margin:10px 0 12px}.v19-gauge span{display:block;height:100%;background:#63b2ee}.v19-feature-row{display:grid;grid-template-columns:1fr 55px;gap:10px;padding:8px 0;border-bottom:1px solid #202f3d}.v19-feature-row span{color:#8b9dad;font-size:.72rem}.v19-feature-row b{text-align:right;color:#dce6ed;font-size:.73rem}.v19-ai-signal{font-size:1.8rem;font-weight:900;letter-spacing:-.03em}.v19-ai-note{color:#8498a9;font-size:.7rem;line-height:1.5;margin-top:5px}
.v19-roadmap{display:grid;grid-template-columns:repeat(5,1fr);border-top:1px solid #294052;border-bottom:1px solid #294052;margin:19px 0 23px}.v19-road-step{padding:18px 13px 17px;position:relative;border-right:1px solid #263846}.v19-road-step:last-child{border-right:0}.v19-road-step:after{content:"→";position:absolute;right:-8px;top:28px;color:#4c708b;background:#0a1016;padding:0 2px}.v19-road-step:last-child:after{display:none}.v19-road-step .n{color:#5d8eb6;font-size:.62rem;font-weight:900}.v19-road-step b{display:block;font-size:.76rem;margin-top:6px}.v19-road-step p{color:#8194a6;font-size:.69rem;line-height:1.5;margin:5px 0 0}.v19-road-step.active{background:#0e1b27}.v19-gates{margin-top:8px}.v19-gate{display:grid;grid-template-columns:125px 1fr;padding:11px 0;border-bottom:1px solid #202f3d}.v19-gate span{color:#6390ae;font-size:.61rem;font-weight:900;letter-spacing:.09em}.v19-gate b{color:#d5e1e9;font-size:.77rem;font-weight:650}.v19-plan-note{border-left:2px solid #607f98;padding-left:15px;color:#8799aa;font-size:.74rem;line-height:1.6;margin:18px 0}
.v19-sim{border:1px solid #2b4052;border-radius:16px;background:#0c141c;padding:21px;margin:17px 0}.v19-sim-flow{display:grid;grid-template-columns:1fr 90px 1fr;align-items:center;gap:15px}.v19-sim-state{padding:16px;border:1px solid #2b3e4e;border-radius:10px;background:#0a1118}.v19-sim-state.target{border-color:#3d6c58;background:#0b1713}.v19-sim-state span{display:block;color:#68869f;font-size:.59rem;font-weight:900;letter-spacing:.1em}.v19-sim-state b{display:block;font-size:1.25rem;margin-top:7px}.v19-sim-state p{color:#8598a9;font-size:.72rem;margin:5px 0 0}.v19-sim-arrow{text-align:center;font-size:1.8rem;color:#6fb5e9}.v19-sim-consequence{display:grid;grid-template-columns:1fr 1fr;gap:24px;margin-top:19px;padding-top:17px;border-top:1px solid #243744}.v19-conclusion{border-left:3px solid #61b5ed;padding:3px 0 3px 16px;margin-top:22px}.v19-conclusion.blocked{border-left-color:#a86670}.v19-conclusion span{display:block;color:#6baedf;font-size:.6rem;font-weight:900;letter-spacing:.11em}.v19-conclusion h2{font-size:1.15rem;margin:5px 0}.v19-conclusion p{color:#91a3b3;font-size:.78rem;line-height:1.6;margin:0}.v19-checks{margin-top:13px}.v19-check{padding:9px 0;border-bottom:1px solid #202f3d;color:#c1ced8;font-size:.74rem}.v19-check:before{content:"✓";color:#64d29b;font-weight:900;margin-right:9px}.v19-conflict{padding:9px 0;border-bottom:1px solid #202f3d;color:#c8b583;font-size:.74rem}.v19-conflict:before{content:"!";color:#d7b969;font-weight:900;margin-right:9px}
.v19-footer{border-top:1px solid #223340;margin-top:35px;padding:13px 0;color:#627789;font-size:.63rem;display:flex;justify-content:space-between;gap:10px}


/* V22 readability pass: remove tiny-text UI and make meaning readable at normal zoom */
.v20-home-hero{padding:48px 52px}
.v20-home-hero h1{font-size:3.35rem;line-height:1.06;max-width:1120px}
.v20-home-hero>p{font-size:1.08rem;line-height:1.72;max-width:1050px}
.v20-home-answer{max-width:1120px;margin-top:28px;padding-top:19px}
.v20-home-answer span{font-size:.76rem}
.v20-home-answer b{font-size:1.22rem;line-height:1.5}
.v20-home-flow{gap:11px;margin-top:28px}
.v20-home-flow>div{padding:11px 13px}
.v20-home-flow strong{font-size:.72rem}
.v20-home-flow b{font-size:.78rem}
.v20-home-flow span{font-size:.72rem}
.v20-home-flow i{font-size:1rem}
.v21-home-propagation{padding:24px 26px;gap:32px}
.v21-prop-intro span{font-size:.72rem}
.v21-prop-intro h3{font-size:1.35rem;line-height:1.4}
.v21-prop-intro p{font-size:.88rem;line-height:1.65}
.v21-prop-chain{gap:12px}
.v21-prop-chain>div{min-width:145px;padding:11px 10px 0}
.v21-prop-chain b{font-size:.70rem}
.v21-prop-chain span{font-size:.73rem;line-height:1.45}
.v21-prop-chain i{font-size:1.25rem}
.v20-section-head{margin-bottom:16px}
.v20-section-head>div>span{font-size:.72rem}
.v20-section-head h2{font-size:1.62rem}
.v20-section-head>p{font-size:.82rem;line-height:1.6}
.v20-home-steps>div{padding:21px 18px;min-height:132px}
.v20-home-steps strong{font-size:.72rem}
.v20-home-steps b{font-size:.96rem;margin-top:7px}
.v20-home-steps span{font-size:.84rem;margin-top:7px;line-height:1.4}
.v20-home-steps small{font-size:.75rem;line-height:1.5;margin-top:6px}
.v20-research{margin-top:38px;padding-top:25px}
.v20-research-head>div>span{font-size:.72rem}
.v20-research-head h2{font-size:1.45rem}
.v20-research-head>p{font-size:.8rem;line-height:1.6}
.v20-research-grid{gap:30px;margin-top:20px}
.v20-research-grid>div{padding:18px 4px 20px}
.v20-research-grid b{font-size:.72rem}
.v20-research-grid p{font-size:.84rem;line-height:1.65;margin:8px 0 12px}
.v20-research-grid a{font-size:.76rem}
.v20-boundary{margin-top:30px;padding:22px 0;gap:38px}
.v20-boundary span{font-size:.70rem}
.v20-boundary h3{font-size:1.18rem}
.v20-boundary p{font-size:.82rem;line-height:1.65}
.v21-vertical-note span{font-size:.68rem}
.v21-vertical-note h4{font-size:1rem}
.v21-vertical-note p{font-size:.82rem}
.v21-insight-panel>span{font-size:.68rem}
.v21-insight-panel h3{font-size:1.28rem}
.v21-insight-panel>p{font-size:.84rem}
.v21-insight-line{font-size:.78rem}
.v20-side-head{font-size:.66rem}
.v20-work-step b{font-size:.74rem}
.v20-work-step small{font-size:.65rem}
.v20-field-note p{font-size:.75rem}
.v20-note-source{font-size:.63rem}
.v20-current-stage span{font-size:.64rem}
.v20-current-stage b{font-size:.82rem}
.v20-current-stage small{font-size:.68rem}
.v20-current-stage em{font-size:.62rem}
.v21-trail-row b{font-size:.65rem}
.v21-trail-row em{font-size:.60rem}
@media(max-width:1000px){.v20-home-hero{padding:34px 28px}.v20-home-hero h1{font-size:2.55rem}.v20-home-steps>div{min-height:auto}.v21-prop-chain>div{min-width:125px}}


/* V23 — SIDEBAR RECOVERY + HUMAN-SCALE HOME TYPOGRAPHY */
[data-testid="stHeader"]{display:flex!important;background:transparent!important;border-bottom:0!important;box-shadow:none!important}
[data-testid="stHeader"] button{visibility:visible!important;opacity:1!important}
[data-testid="stSidebar"]{min-width:340px!important}
[data-testid="stSidebar"] .block-container{padding-top:1.1rem!important;padding-bottom:2rem!important}
.v20-home-answer span{font-size:.82rem!important}
.v20-home-answer b{font-size:1.28rem!important;line-height:1.55!important}
.v20-home-flow strong{font-size:.78rem!important}.v20-home-flow b{font-size:.92rem!important}.v20-home-flow span{font-size:.84rem!important}
.v21-prop-intro span{font-size:.78rem!important}.v21-prop-intro h3{font-size:1.42rem!important}.v21-prop-intro p{font-size:.94rem!important;line-height:1.7!important}
.v21-prop-chain b{font-size:.78rem!important}.v21-prop-chain span{font-size:.80rem!important;line-height:1.5!important}
.v20-section-head>div>span{font-size:.78rem!important}.v20-section-head h2{font-size:1.78rem!important}.v20-section-head>p{font-size:.94rem!important;line-height:1.65!important}
.v20-home-steps strong{font-size:.78rem!important}.v20-home-steps b{font-size:1.02rem!important}.v20-home-steps span{font-size:.92rem!important;line-height:1.45!important}.v20-home-steps small{font-size:.84rem!important;line-height:1.55!important}
.v20-research-head>div>span{font-size:.78rem!important}.v20-research-head h2{font-size:1.62rem!important}.v20-research-head>p{font-size:.92rem!important;line-height:1.65!important}
.v20-research-grid b{font-size:.78rem!important}.v20-research-grid p{font-size:.94rem!important;line-height:1.7!important}.v20-research-grid a{font-size:.84rem!important}
.v20-boundary{margin-top:32px!important;padding:25px 0!important;gap:42px!important}.v20-boundary span{font-size:.78rem!important}.v20-boundary h3{font-size:1.32rem!important;line-height:1.4!important}.v20-boundary p{max-width:850px!important;color:#a5b5c4!important;font-size:.96rem!important;line-height:1.72!important}
.v18-footer{font-size:.72rem!important}
.v20-side-head{font-size:.74rem!important}.v20-side-case{font-size:1.08rem!important}.v20-side-id{font-size:.72rem!important}.v20-side-block{padding:15px 0!important}.v20-work-step b{font-size:.82rem!important}.v20-work-step small{font-size:.74rem!important;line-height:1.45!important}.v18-side-metric{font-size:.76rem!important}.v18-side-metric b{font-size:.84rem!important}.v20-field-note p{font-size:.84rem!important;line-height:1.6!important}.v20-note-source{font-size:.70rem!important}.v20-current-stage span{font-size:.72rem!important}.v20-current-stage b{font-size:.92rem!important}.v20-current-stage small{font-size:.78rem!important;line-height:1.5!important}.v20-current-stage em{font-size:.72rem!important;line-height:1.5!important}.v21-trail-row b{font-size:.70rem!important}.v21-trail-row em{font-size:.67rem!important;line-height:1.4!important}

/* V24 — HUMAN-SCALE INVESTIGATION + EXPLICIT MIGRATION CONSEQUENCE */
/* Main investigation pages should read like a report, not like metadata. */
.v19-page-intro h1{font-size:2.85rem!important;line-height:1.12!important}
.v19-page-intro p{font-size:1.02rem!important;line-height:1.72!important;color:#a8b8c7!important}
.v19-finding{padding-left:18px!important;margin:20px 0 26px!important}
.v19-finding span{font-size:.72rem!important}
.v19-finding h2{font-size:1.58rem!important;line-height:1.4!important}
.v19-finding p{font-size:.96rem!important;line-height:1.72!important}
.v19-focus-main span,.v19-focus-stat span{font-size:.68rem!important}
.v19-focus-main b{font-size:1.05rem!important}
.v19-focus-stat b{font-size:1rem!important}
.v19-readout .eyebrow{font-size:.70rem!important}
.v19-readout h3{font-size:1.42rem!important;line-height:1.35!important}
.v19-readout p,.v19-readout li{font-size:.94rem!important;line-height:1.72!important}
.v19-table-caption h3{font-size:1.30rem!important}
.v19-table-caption p{font-size:.88rem!important;line-height:1.55!important}
.v19-table-note{font-size:.70rem!important}
.v19-runtime-head h3{font-size:1.40rem!important}
.v19-runtime-head p{font-size:.90rem!important;line-height:1.65!important}
.v19-runtime-cell span{font-size:.64rem!important}
.v19-runtime-cell b{font-size:.98rem!important}
.v19-runtime-detail{font-size:.84rem!important;line-height:1.7!important}
.v19-graph-reading{font-size:.90rem!important;line-height:1.7!important}
.v19-legend span{font-size:.72rem!important}
.v19-path-node{font-size:.78rem!important;padding:8px 10px!important}
.v19-evidence-line{padding:14px 0!important}
.v19-evidence-line span{font-size:.68rem!important}
.v19-evidence-line b{font-size:.88rem!important}
.v19-evidence-line p{font-size:.82rem!important;line-height:1.6!important}
.v19-assess-block h3{font-size:1.18rem!important}
.v19-assess-block p{font-size:.90rem!important;line-height:1.7!important}
.v19-feature-row span,.v19-feature-row b{font-size:.82rem!important}
.v19-ai-note{font-size:.82rem!important;line-height:1.6!important}
.v19-road-step .n{font-size:.72rem!important}.v19-road-step b{font-size:.92rem!important}.v19-road-step p{font-size:.80rem!important;line-height:1.6!important}
.v19-gate span{font-size:.69rem!important}.v19-gate b{font-size:.88rem!important;line-height:1.55!important}
.v19-plan-note{font-size:.86rem!important;line-height:1.7!important}
.v19-sim{padding:24px!important}
.v19-sim-state span{font-size:.67rem!important}.v19-sim-state b{font-size:1.38rem!important}.v19-sim-state p{font-size:.82rem!important}
.v19-sim-consequence{font-size:.94rem!important}.v19-sim-consequence p{font-size:.84rem!important;line-height:1.6!important}
.v19-conclusion{padding:18px 0!important}.v19-conclusion span{font-size:.70rem!important}.v19-conclusion h2{font-size:1.38rem!important}.v19-conclusion p{font-size:.90rem!important;line-height:1.7!important}
.v19-check,.v19-conflict{font-size:.88rem!important;line-height:1.6!important;padding:12px 0!important}
.v21-vertical-note{gap:15px!important;margin:18px 0!important}
.v21-vertical-note span{font-size:.68rem!important}.v21-vertical-note h4{font-size:1.08rem!important}.v21-vertical-note p{font-size:.86rem!important;line-height:1.72!important}
.v21-insight-panel>span{font-size:.68rem!important}.v21-insight-panel h3{font-size:1.28rem!important}.v21-insight-panel>p{font-size:.88rem!important;line-height:1.7!important}.v21-insight-line{font-size:.80rem!important}
.v21-transition-note{font-size:.86rem!important;line-height:1.7!important}
.v21-assess-primary>span,.v21-ai-panel>span{font-size:.67rem!important}.v21-assess-primary>p,.v21-ai-panel>p{font-size:.84rem!important;line-height:1.7!important}.v21-factor{font-size:.82rem!important}
.v21-stage-conclusion>span{font-size:.68rem!important}.v21-stage-conclusion>b{font-size:1rem!important}.v21-stage-conclusion p{font-size:.84rem!important;line-height:1.7!important}
.v21-case-finding span{font-size:.68rem!important}.v21-case-finding b{font-size:1rem!important}.v21-case-finding p{font-size:.82rem!important;line-height:1.6!important}
.v21-trail-row b{font-size:.75rem!important}.v21-trail-row em{font-size:.72rem!important;line-height:1.45!important}
/* Streamlit tables: make evidence readable without changing their data. */
[data-testid="stDataFrame"] div[role="gridcell"], [data-testid="stDataFrame"] div[role="columnheader"]{font-size:15px!important}
[data-testid="stDataFrame"]{font-size:15px!important}
/* V25 — readability and consequence-first presentation */

/* V25 controls: prevent clipped action text and tiny form labels. */
.stButton>button{font-size:1rem!important;line-height:1.35!important;min-height:48px!important;padding:10px 16px!important;white-space:normal!important}
[data-testid="stSelectbox"] label,[data-testid="stRadio"] label,[data-testid="stCheckbox"] label{font-size:.98rem!important;font-weight:700!important}
[data-testid="stSelectbox"] div[data-baseweb="select"]{font-size:1rem!important}

.v19-page-intro h1{font-size:3.05rem!important}
.v19-page-intro p{font-size:1.08rem!important}
.v19-finding span,.v24-kicker,.v24-change-banner span,.v24-consequence-box>span{font-size:.82rem!important}
.v19-finding h2{font-size:1.72rem!important}
.v19-finding p{font-size:1.05rem!important}
.v19-focus-main span,.v19-focus-stat span{font-size:.76rem!important}
.v19-focus-main b{font-size:1.15rem!important}.v19-focus-stat b{font-size:1.08rem!important}
.v19-readout .eyebrow{font-size:.78rem!important}.v19-readout h3{font-size:1.52rem!important}.v19-readout p,.v19-readout li{font-size:1.02rem!important;line-height:1.78!important}
.v19-table-caption h3{font-size:1.42rem!important}.v19-table-caption p{font-size:.98rem!important;line-height:1.65!important}
.v19-runtime-head h3{font-size:1.52rem!important}.v19-runtime-head p{font-size:1rem!important;line-height:1.75!important}
.v19-runtime-cell span{font-size:.72rem!important}.v19-runtime-cell b{font-size:1.08rem!important}.v19-runtime-detail{font-size:.92rem!important}
.v19-graph-reading{font-size:1rem!important}.v19-legend span{font-size:.80rem!important}.v19-path-node{font-size:.90rem!important;padding:10px 13px!important}
.v19-evidence-line span{font-size:.74rem!important}.v19-evidence-line b{font-size:.98rem!important}.v19-evidence-line p{font-size:.92rem!important}
.v19-assess-block h3{font-size:1.28rem!important}.v19-assess-block p{font-size:.98rem!important}
.v19-road-step .n{font-size:.78rem!important}.v19-road-step b{font-size:1rem!important}.v19-road-step p{font-size:.90rem!important}
.v19-gate span{font-size:.76rem!important}.v19-gate b{font-size:.98rem!important}.v19-plan-note{font-size:.96rem!important}
.v19-sim-state span{font-size:.74rem!important}.v19-sim-state b{font-size:1.52rem!important}.v19-sim-state p{font-size:.94rem!important}.v19-sim-consequence{font-size:1rem!important}.v19-sim-consequence p{font-size:.94rem!important}
.v19-conclusion span{font-size:.80rem!important}.v19-conclusion h2{font-size:1.58rem!important}.v19-conclusion p{font-size:1rem!important;line-height:1.78!important}
.v19-check,.v19-conflict{font-size:1rem!important;line-height:1.7!important;padding:15px 0!important}
.v21-vertical-note span{font-size:.78rem!important}.v21-vertical-note h4{font-size:1.22rem!important}.v21-vertical-note p{font-size:.98rem!important;line-height:1.8!important}
.v21-insight-panel>span{font-size:.76rem!important}.v21-insight-panel h3{font-size:1.38rem!important}.v21-insight-panel>p{font-size:.96rem!important}.v21-insight-line{font-size:.90rem!important}
.v21-transition-note{font-size:.96rem!important}.v21-stage-conclusion>span{font-size:.76rem!important}.v21-stage-conclusion>b{font-size:1.10rem!important}.v21-stage-conclusion p{font-size:.94rem!important}
.v21-case-finding span{font-size:.76rem!important}.v21-case-finding b{font-size:1.08rem!important}.v21-case-finding p{font-size:.92rem!important}
.v21-trail-row b{font-size:.82rem!important}.v21-trail-row em{font-size:.80rem!important}
/* V25: consequence and runtime surfaces */
.v25-result-hero{border:1px solid #4b789b;background:linear-gradient(145deg,#122332,#0b141d);border-radius:18px;padding:26px 30px;margin:28px 0 30px}
.v25-result-hero .kicker{font-size:.82rem;color:#72bdf2;font-weight:900;letter-spacing:.15em}.v25-result-hero h2{font-size:2rem;line-height:1.2;margin:8px 0 8px}.v25-result-hero p{font-size:1.08rem;line-height:1.75;color:#b2c2d0;margin:0;max-width:1000px}
.v25-runtime-title{font-size:1.65rem!important}.v25-runtime-copy{font-size:1.03rem!important;line-height:1.78!important}
.v25-runtime-grid{display:grid;grid-template-columns:repeat(4,1fr);border:1px solid #30485d;border-radius:16px;overflow:hidden;background:#0d151e;margin-top:20px}
.v25-runtime-card{padding:20px;border-right:1px solid #263b4d;min-height:110px}.v25-runtime-card:last-child{border-right:0}.v25-runtime-card span{display:block;font-size:.75rem;color:#70b9ee;font-weight:900;letter-spacing:.11em;margin-bottom:8px}.v25-runtime-card b{font-size:1.22rem;color:#edf5fa;line-height:1.3}.v25-runtime-card small{display:block;font-size:.90rem;color:#9fb1c1;margin-top:5px;line-height:1.5}
.v25-runtime-evidence{margin-top:18px;padding:20px;border:1px solid #293f52;border-radius:14px;background:#0b131b}.v25-runtime-evidence h4{font-size:1.18rem;margin:0 0 12px}.v25-runtime-evidence p{font-size:.98rem;line-height:1.7;color:#a9bac8}.v25-runtime-evidence li{font-size:.95rem;line-height:1.65;color:#d1dde6}
.v25-consequence{background:linear-gradient(145deg,#132331,#0b141c);border:1px solid #4a7394;border-radius:19px;padding:30px 32px;margin:34px 0 24px}.v25-consequence-header{display:flex;justify-content:space-between;gap:20px;align-items:flex-start;border-bottom:1px solid #31495b;padding-bottom:20px}.v25-consequence-header h2{font-size:2rem;line-height:1.22;margin:7px 0}.v25-consequence-header p{font-size:1rem;line-height:1.65;color:#a9bac7;margin:0}.v25-status{font-size:.78rem;font-weight:900;letter-spacing:.08em;padding:9px 13px;border-radius:999px;border:1px solid #3b6685;background:#0d1a25;white-space:nowrap;color:#b9def6}
.v25-change{border-left:4px solid #6dbcf2;padding:4px 0 4px 20px;margin:22px 0 24px}.v25-change span{font-size:.78rem;color:#70b9ee;font-weight:900;letter-spacing:.12em}.v25-change b{display:block;font-size:1.45rem;line-height:1.4;margin-top:6px}.v25-change p{font-size:1rem;line-height:1.7;color:#aabcca;margin:7px 0 0}
.v25-decision-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:0;border-top:1px solid #30485b;border-bottom:1px solid #30485b}.v25-decision{padding:22px 24px 22px 0;min-height:205px}.v25-decision+.v25-decision{border-left:1px solid #30485b;padding-left:24px}.v25-decision span{font-size:.80rem;color:#70b9ee;font-weight:900;letter-spacing:.11em}.v25-decision h3{font-size:1.28rem;margin:8px 0 12px}.v25-decision ul{margin:0;padding-left:21px}.v25-decision li{font-size:1rem;line-height:1.7;color:#b5c5d1;margin:5px 0}.v25-bottom-line{margin-top:22px;border:1px solid #47718e;border-radius:13px;padding:20px 22px;background:#0b1823}.v25-bottom-line span{font-size:.78rem;color:#70b9ee;font-weight:900;letter-spacing:.12em}.v25-bottom-line b{display:block;font-size:1.35rem;line-height:1.45;margin-top:7px;color:#eff6fa}.v25-bottom-line p{font-size:1rem;line-height:1.7;color:#a9bac7;margin:7px 0 0}
/* V26 refinement */
.v26-runtime-kpi-grid{display:grid;grid-template-columns:repeat(4,1fr);border:1px solid #30485d;border-radius:16px;overflow:hidden;background:#0d151e;margin-top:20px}.v26-runtime-kpi{padding:22px;border-right:1px solid #263b4d;min-height:128px}.v26-runtime-kpi:last-child{border-right:0}.v26-runtime-kpi span,.v26-runtime-story>div>span,.v26-runtime-section-title>span,.v26-assess-why span,.v26-assess-why-grid b,.v26-sim-action-note span,.v26-result-lead span,.v26-final-decision>span{display:block;font-size:.78rem;color:#70b9ee;font-weight:900;letter-spacing:.12em}.v26-runtime-kpi b{display:block;font-size:1.38rem;line-height:1.25;margin-top:7px}.v26-runtime-kpi small{display:block;font-size:.96rem;color:#9fb1c1;margin-top:7px;line-height:1.5}.v26-runtime-story{display:grid;grid-template-columns:1.35fr .65fr;gap:28px;margin-top:20px;padding:24px 26px;border:1px solid #30485d;border-radius:16px;background:linear-gradient(145deg,#101c27,#0b141c)}.v26-runtime-story h3{font-size:1.45rem;margin:7px 0}.v26-runtime-story p{font-size:1rem;line-height:1.75;color:#a9bac8;margin:0}.v26-runtime-facts{display:grid;grid-template-columns:1fr 1fr;border-left:1px solid #2c4254;padding-left:24px}.v26-runtime-facts>div{padding:8px 12px;border-bottom:1px solid #253a4b}.v26-runtime-facts b{display:block;font-size:.82rem;color:#7da5c2}.v26-runtime-facts span{font-size:.92rem!important;color:#d5e1ea!important;letter-spacing:0!important;margin-top:4px}.v26-runtime-section-title{margin-top:25px;margin-bottom:8px}.v26-runtime-section-title h3{font-size:1.35rem;margin:6px 0}.v26-runtime-section-title p{font-size:.98rem;line-height:1.6;color:#91a5b5;margin:0}.v26-assess-why{margin:10px 0 24px;padding:24px 26px;border:1px solid #2f475a;border-radius:16px;background:linear-gradient(145deg,#0f1b25,#0a131b)}.v26-assess-why-head h2{font-size:1.45rem;line-height:1.3;margin:7px 0 18px}.v26-assess-why-grid{display:grid;grid-template-columns:repeat(4,1fr);border-top:1px solid #293d4d}.v26-assess-why-grid>div{padding:17px 18px 7px 0}.v26-assess-why-grid>div+div{padding-left:18px;border-left:1px solid #293d4d}.v26-assess-why-grid b{font-size:.72rem}.v26-assess-why-grid p{font-size:.94rem;line-height:1.65;color:#a1b3c1;margin:8px 0 0}.v26-sim-action-note{margin:18px 0 8px;padding:18px 20px;border-left:3px solid #68b7ec;background:#0c1822}.v26-sim-action-note b{display:block;font-size:1.12rem;margin-top:5px}.v26-sim-action-note p{font-size:.98rem;line-height:1.65;color:#9eb0bf;margin:7px 0 0}.v26-result-lead{margin:22px 0 14px;padding:18px 20px;border:1px solid #35546b;border-radius:12px;background:#0b1721}.v26-result-lead b{display:block;font-size:1.2rem;margin-top:5px}.v26-result-lead p{font-size:.98rem;line-height:1.6;color:#9eafbd;margin:5px 0 0}.v26-final-decision{margin-top:22px;padding:24px 26px;border:1px solid #4c7898;border-radius:15px;background:linear-gradient(145deg,#122433,#0a141c)}.v26-final-decision h3{font-size:1.5rem;margin:7px 0 17px}.v26-final-points{display:grid;grid-template-columns:repeat(4,1fr);border-top:1px solid #2d4658;border-bottom:1px solid #2d4658}.v26-final-points>div{padding:15px 14px 15px 0}.v26-final-points>div+div{border-left:1px solid #2d4658;padding-left:14px}.v26-final-points b{display:block;font-size:.72rem;color:#74b8e9;letter-spacing:.09em}.v26-final-points span{display:block;font-size:.95rem!important;line-height:1.55;color:#d4e0e8!important;letter-spacing:0!important;margin-top:6px}.v26-final-answer{margin-top:18px;padding:16px 18px;background:#09131c;border:1px solid #2d4658;border-radius:10px;font-size:1rem;line-height:1.7;color:#b7c8d4}.v26-final-answer b{color:#eef5f9}.v19-conclusion,.v25-consequence,.v25-result-hero,.v26-final-decision{overflow-wrap:anywhere}
@media(max-width:1000px){.v25-runtime-grid,.v26-runtime-kpi-grid{grid-template-columns:1fr 1fr}.v25-runtime-card:nth-child(2),.v26-runtime-kpi:nth-child(2){border-right:0}.v25-runtime-card,.v26-runtime-kpi{border-bottom:1px solid #263b4d}.v25-decision-grid,.v26-assess-why-grid,.v26-final-points{grid-template-columns:1fr}.v25-decision+.v25-decision,.v26-assess-why-grid>div+div,.v26-final-points>div+div{border-left:0;border-top:1px solid #30485b;padding-left:0}.v25-consequence-header{flex-direction:column}.v25-consequence-header h2{font-size:1.65rem}.v26-runtime-story{grid-template-columns:1fr}.v26-runtime-facts{border-left:0;border-top:1px solid #2c4254;padding:15px 0 0}.v26-final-points>div{padding-right:0}}
/* V24 consequence card */
.v24-consequence-card{background:linear-gradient(145deg,#132331,#0b141c 72%);border:1px solid #4a7394;border-radius:19px;padding:28px 30px;margin:30px 0 20px;box-shadow:0 22px 55px rgba(0,0,0,.20)}
.v24-consequence-top{display:flex;justify-content:space-between;align-items:flex-start;gap:20px;border-bottom:1px solid #294050;padding-bottom:18px}
.v24-kicker{display:block;color:#70b9ef;font-size:.72rem;font-weight:900;letter-spacing:.14em}
.v24-consequence-top h2{font-size:1.70rem;line-height:1.3;margin:6px 0 0;max-width:850px}
.v24-status{border:1px solid #355e7d;background:#0d1b27;border-radius:999px;padding:7px 11px;color:#a9d5f2;font-size:.70rem;font-weight:850;white-space:nowrap}
.v24-change-banner{border-left:4px solid #69b8ef;padding:8px 0 8px 18px;margin:21px 0 23px}
.v24-change-banner span,.v24-consequence-box>span{display:block;color:#70b7e9;font-size:.68rem;font-weight:900;letter-spacing:.11em}
.v24-change-banner b{display:block;color:#eef5fa;font-size:1.22rem;line-height:1.45;margin-top:5px}
.v24-change-banner p{color:#9eb0bf;font-size:.90rem;line-height:1.65;margin:5px 0 0}
.v24-consequence-grid{display:grid;grid-template-columns:1fr 1fr;gap:0;border-top:1px solid #294050}
.v24-consequence-box{padding:19px 20px 19px 0;border-bottom:1px solid #294050}
.v24-consequence-box:nth-child(even){padding-left:22px;border-left:1px solid #294050}
.v24-consequence-box b{display:block;font-size:1.02rem;color:#e5eef4;margin:6px 0 6px}
.v24-consequence-box p{font-size:.88rem;color:#9bafbf;line-height:1.72;margin:0;max-width:650px}
.v24-consequence-answer{border-bottom:0!important;padding-bottom:5px!important}
.v24-consequence-answer b{font-size:1.10rem!important}
.v24-read-this{border-top:1px solid #355064;margin-top:15px;padding-top:15px;color:#91a7b8;font-size:.82rem;line-height:1.7}
.v24-read-this b,.v24-read-this strong{color:#dbe8ef}
@media(max-width:1000px){.v24-consequence-top{flex-direction:column}.v24-consequence-grid{grid-template-columns:1fr}.v24-consequence-box:nth-child(even){padding-left:0;border-left:0}.v24-consequence-box{padding-right:0}.v24-consequence-answer{padding-bottom:0!important}.v24-consequence-top h2{font-size:1.45rem}}

/* V32 interaction surfaces */
.v32-control-wrap{margin:16px 0 24px;padding:14px 16px 12px;border:1px solid #315069;border-radius:15px;background:linear-gradient(135deg,#0e1a24,#0a1219)}
.v32-control-head{display:flex;justify-content:space-between;gap:15px;align-items:center;margin-bottom:8px}.v32-control-head span,.v32-plan-level span,.v32-plan-evidence span{display:block;color:#70b9ee;font-size:.63rem;font-weight:900;letter-spacing:.12em}.v32-control-head b{display:block;font-size:.93rem;margin-top:3px}.v32-control-head small{color:#7890a3;font-size:.66rem}.v32-control-status{height:100%;padding:10px 12px;border:1px solid #294458;border-radius:10px;background:#0a141c}.v32-control-status span{display:block;color:#6bb6e8;font-size:.58rem;font-weight:900;letter-spacing:.1em}.v32-control-status b{display:block;font-size:.85rem;margin-top:5px}.v32-control-status small{display:block;color:#8fa3b3;font-size:.68rem;margin-top:4px}
.v32-case-quick{display:grid;grid-template-columns:1fr 1fr 1fr;border:1px solid #2e4556;border-radius:15px;overflow:hidden;margin:17px 0 21px;background:#0b151d}.v32-case-quick>div{padding:17px 18px;border-right:1px solid #2e4556}.v32-case-quick>div:last-child{border-right:0}.v32-case-quick span{display:block;color:#6fb6e8;font-size:.62rem;font-weight:900;letter-spacing:.11em}.v32-case-quick b{display:block;font-size:.9rem;margin-top:5px}.v32-case-quick small{display:block;color:#8ea2b2;font-size:.72rem;line-height:1.5;margin-top:4px}
.v32-bridge-caption{margin:22px 0 6px;padding:14px 17px;border:1px solid #2d485a;border-radius:12px;background:#0b151d}.v32-bridge-caption span{display:block;color:#6fb6e8;font-size:.62rem;font-weight:900;letter-spacing:.11em}.v32-bridge-caption b{display:block;font-size:.9rem;margin-top:4px}.v32-bridge-caption small{display:block;color:#8197a7;font-size:.69rem;margin-top:3px}
.v32-trace-tech{display:grid;grid-template-columns:repeat(4,1fr);gap:0;margin:19px 0;border:1px solid #2d4657;border-radius:13px;overflow:hidden;background:#0b151d}.v32-trace-tech>div{padding:15px 16px;border-right:1px solid #2d4657}.v32-trace-tech>div:last-child{border-right:0}.v32-trace-tech span{display:block;color:#6fb6e8;font-size:.57rem;font-weight:900;letter-spacing:.1em}.v32-trace-tech b{display:block;font-size:.9rem;margin-top:5px}.v32-trace-tech small{display:block;color:#8298a8;font-size:.67rem;line-height:1.45;margin-top:4px}
.v32-ai-lab{margin-top:23px;border:1px solid #3c6380;border-radius:17px;background:linear-gradient(145deg,#0d1b25,#091219);overflow:hidden}.v32-ai-lab-head{padding:18px 20px;border-bottom:1px solid #2e4b5d}.v32-ai-lab-head span{display:block;color:#70b9ee;font-size:.65rem;font-weight:900;letter-spacing:.12em}.v32-ai-lab-head b{display:block;font-size:1.15rem;margin-top:5px}.v32-ai-lab-head small{display:block;color:#8ea3b2;font-size:.72rem;line-height:1.5;margin-top:4px}.v32-ai-proof{display:grid;grid-template-columns:repeat(3,1fr);border-bottom:1px solid #2e4b5d}.v32-ai-proof>div{padding:15px 18px;border-right:1px solid #2e4b5d}.v32-ai-proof>div:last-child{border-right:0}.v32-ai-proof span{display:block;color:#6fb6e8;font-size:.58rem;font-weight:900;letter-spacing:.1em}.v32-ai-proof b{display:block;font-size:1.15rem;margin-top:5px}.v32-ai-proof small{display:block;color:#8298a8;font-size:.67rem;margin-top:3px}
.v32-handoff{display:grid;grid-template-columns:1.1fr .9fr;margin:20px 0;border:1px solid #2d4657;border-radius:14px;overflow:hidden;background:#0b151d}.v32-handoff>div{padding:18px 20px}.v32-handoff>div+div{border-left:1px solid #2d4657}.v32-handoff span{display:block;color:#6fb6e8;font-size:.61rem;font-weight:900;letter-spacing:.1em}.v32-handoff b{display:block;font-size:.94rem;margin-top:5px}.v32-handoff small{display:block;color:#91a4b2;font-size:.72rem;line-height:1.55;margin-top:5px}
.v32-plan-level{margin:20px 0 7px;padding:16px 18px;border-left:3px solid #6fb6e8;background:#0b151d}.v32-plan-level h3{font-size:1.15rem;margin:5px 0}.v32-plan-level p{font-size:.78rem;line-height:1.55;color:#91a4b2;margin:0}.v32-plan-evidence{margin:18px 0;padding:16px 18px;border:1px solid #2f4a5c;border-radius:12px;background:#0a141c}.v32-plan-evidence b{display:block;font-size:.9rem;margin-top:5px}.v32-plan-evidence small{display:block;color:#879baa;font-size:.7rem;line-height:1.5;margin-top:4px}
@media(max-width:900px){.v32-case-quick,.v32-ai-proof,.v32-handoff{grid-template-columns:1fr}.v32-case-quick>div,.v32-ai-proof>div{border-right:0;border-bottom:1px solid #2e4556}.v32-trace-tech{grid-template-columns:1fr 1fr}.v32-trace-tech>div:nth-child(2){border-right:0}.v32-trace-tech>div:nth-child(n+3){border-top:1px solid #2d4657}}

/* V33 surgical clarity / proof surfaces */
.v33-tech-overview{margin:18px 0 22px;padding:20px 22px;border:1px solid #315069;border-radius:16px;background:linear-gradient(145deg,#0d1b25,#091219)}
.v33-tech-head{display:flex;justify-content:space-between;gap:15px;align-items:flex-start;border-bottom:1px solid #294454;padding-bottom:13px}.v33-tech-head span,.v33-tech-grid span,.v33-stack span,.v33-ai-proofline span{display:block;color:#70b9ee;font-size:.62rem;font-weight:900;letter-spacing:.12em}.v33-tech-head h3{margin:5px 0 0;font-size:1.25rem}.v33-tech-head small{color:#8096a7;font-size:.7rem}.v33-tech-grid{display:grid;grid-template-columns:repeat(4,1fr);margin-top:14px}.v33-tech-grid>div{padding:8px 16px 8px 0}.v33-tech-grid>div+div{border-left:1px solid #294454;padding-left:16px}.v33-tech-grid b{display:block;font-size:.94rem;margin-top:5px}.v33-tech-grid p{font-size:.76rem;line-height:1.55;color:#92a6b5;margin:5px 0 0}.v33-stack{margin-top:12px;padding:11px 13px;background:#081119;border:1px solid #253d4d;border-radius:9px}.v33-stack b{font-size:.78rem;margin-top:4px;display:block;color:#d8e5ec}
.v33-ai-proofline{display:grid;grid-template-columns:repeat(4,1fr);border-top:1px solid #294454;border-bottom:1px solid #294454;background:#09131b;margin:0 0 12px}.v33-ai-proofline>div{padding:13px 14px}.v33-ai-proofline>div+div{border-left:1px solid #263f50}.v33-ai-proofline b{display:block;font-size:.86rem;margin-top:4px}.v33-ai-proofline small{display:block;color:#8fa3b2;font-size:.68rem;line-height:1.45;margin-top:3px}.v33-trace-engine{margin:12px 0 18px;padding:12px 15px;border:1px solid #29495d;border-radius:10px;background:#09151e}.v33-trace-engine span{display:block;color:#70b9ee;font-size:.62rem;font-weight:900;letter-spacing:.12em}.v33-trace-engine b{display:block;font-size:.82rem;margin-top:4px}.v33-trace-engine small{display:block;color:#8fa4b4;font-size:.72rem;margin-top:4px}.v33-sim-conclusion{margin:24px 0;border:1px solid #4b7087;border-radius:18px;background:linear-gradient(145deg,#102532,#0a151e);overflow:hidden}.v33-sim-conclusion.blocked{border-color:#81525b}.v33-sim-conclusion-top{display:flex;justify-content:space-between;gap:18px;padding:24px 26px;border-bottom:1px solid #2d4758;align-items:flex-start}.v33-sim-conclusion-top span{color:#70b9ee;font-size:.68rem;font-weight:900;letter-spacing:.12em}.v33-sim-conclusion-top h2{font-size:1.35rem;line-height:1.45;margin:7px 0 0;max-width:930px}.v33-status-pill{padding:8px 12px;border:1px solid #4a6d83;border-radius:999px;color:#d9ebf4;font-size:.68rem;font-weight:900;white-space:nowrap;background:#0b1822}.v33-sim-facts{display:grid;grid-template-columns:repeat(4,1fr)}.v33-sim-facts>div{padding:16px 18px;min-height:100px}.v33-sim-facts>div+div{border-left:1px solid #2a4353}.v33-sim-facts span{display:block;color:#6da9d2;font-size:.62rem;font-weight:900;letter-spacing:.1em}.v33-sim-facts b{display:block;font-size:.9rem;margin-top:6px;line-height:1.4}.v33-sim-facts small{display:block;color:#91a5b5;font-size:.72rem;line-height:1.45;margin-top:4px}
@media(max-width:1000px){.v33-tech-grid,.v33-ai-proofline,.v33-sim-facts{grid-template-columns:1fr 1fr}.v33-tech-grid>div+div,.v33-ai-proofline>div+div,.v33-sim-facts>div+div{border-left:0}.v33-tech-grid>div:nth-child(n+3),.v33-ai-proofline>div:nth-child(n+3),.v33-sim-facts>div:nth-child(n+3){border-top:1px solid #294454}.v33-sim-conclusion-top{flex-direction:column}}
@media(max-width:650px){.v33-tech-grid,.v33-ai-proofline,.v33-sim-facts{grid-template-columns:1fr}}

/* V34 targeted readability fixes */
.v33-sim-conclusion-top h2{font-size:1.22rem!important;line-height:1.38!important;font-weight:700!important;max-width:900px!important}
.v33-sim-conclusion-top{padding:20px 22px!important}
.v33-sim-facts>div{min-height:86px!important;padding:13px 15px!important}
.v33-sim-facts b{font-size:.82rem!important}
.v33-sim-facts small{font-size:.67rem!important}
.v33-sim-conclusion{margin:18px 0!important}
@media(max-width:1000px){.v33-sim-conclusion-top h2{font-size:1.08rem!important}}

/* V35 PLAN orchestration surfaces */
.v33-plan-command{display:grid;grid-template-columns:1.35fr .95fr;margin:18px 0 24px;border:1px solid #35566d;border-radius:18px;overflow:hidden;background:linear-gradient(145deg,#102331,#09131b)}
.v33-plan-command-main{padding:22px 24px;border-right:1px solid #2b4658}.v33-plan-command-main>span,.v33-section-head>span,.v33-plan-command-stats span,.v33-gate-top em,.v33-gate-card>small,.v33-evidence-map>div>span,.v33-plan-handoff span{display:block;color:#70b9ee;font-size:.62rem;font-weight:900;letter-spacing:.12em}.v33-plan-command-main h2{margin:6px 0 7px;font-size:1.45rem;letter-spacing:.01em}.v33-plan-command-main p{margin:0;color:#9eb2c0;font-size:.82rem;line-height:1.55}.v33-plan-command-stats{display:grid;grid-template-columns:1fr 1fr}.v33-plan-command-stats>div{padding:15px 16px}.v33-plan-command-stats>div:nth-child(odd){border-right:1px solid #294454}.v33-plan-command-stats>div:nth-child(n+3){border-top:1px solid #294454}.v33-plan-command-stats b{display:block;font-size:1rem;margin-top:4px}.v33-plan-command-stats small{display:block;color:#8197a7;font-size:.68rem;margin-top:3px}
.v33-section-head{margin:25px 0 9px;padding-left:2px}.v33-section-head h3{margin:5px 0 4px;font-size:1.13rem}.v33-section-head p{margin:0;max-width:980px;color:#8fa4b3;font-size:.76rem;line-height:1.55}
.v33-gate-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:9px;margin:10px 0 24px}.v33-gate-card{min-height:145px;padding:15px 16px;border:1px solid #294657;border-radius:13px;background:#0a151d}.v33-gate-top{display:flex;justify-content:space-between;gap:8px;align-items:center}.v33-gate-top>span{width:26px;height:26px;border:1px solid #41677e;border-radius:50%;display:flex;align-items:center;justify-content:center;color:#bfe3f6;font-size:.63rem;font-weight:900}.v33-gate-top em{font-style:normal;color:#8fb4c9;font-size:.55rem}.v33-gate-card>b{display:block;margin-top:12px;font-size:.82rem}.v33-gate-card p{color:#91a6b5;font-size:.7rem;line-height:1.48;margin:5px 0 9px}.v33-gate-card>small{color:#66889d;font-size:.53rem;letter-spacing:.1em}
.v33-evidence-map{display:grid;grid-template-columns:repeat(4,1fr);border:1px solid #2d4859;border-radius:14px;overflow:hidden;background:#0a151d;margin:10px 0 18px}.v33-evidence-map>div{padding:16px}.v33-evidence-map>div+div{border-left:1px solid #2d4859}.v33-evidence-map>div>b{display:block;font-size:.78rem;line-height:1.4;margin-top:5px}.v33-evidence-map>div>p{color:#899eae;font-size:.68rem;line-height:1.48;margin:6px 0 0}
.v33-plan-handoff{display:grid;grid-template-columns:1.1fr .9fr;margin:22px 0 12px;border:1px solid #3b6076;border-radius:15px;overflow:hidden;background:linear-gradient(145deg,#0e1e29,#09131b)}.v33-plan-handoff>div{padding:17px 19px}.v33-plan-handoff>div+div{border-left:1px solid #2d4859}.v33-plan-handoff b{display:block;font-size:.9rem;margin-top:5px}.v33-plan-handoff small{display:block;color:#91a5b4;font-size:.7rem;line-height:1.5;margin-top:4px}
@media(max-width:950px){.v33-plan-command{grid-template-columns:1fr}.v33-plan-command-main{border-right:0;border-bottom:1px solid #2b4658}.v33-gate-grid,.v33-evidence-map{grid-template-columns:1fr 1fr}.v33-evidence-map>div:nth-child(odd){border-left:0}.v33-evidence-map>div:nth-child(n+3){border-top:1px solid #2d4859}.v33-plan-handoff{grid-template-columns:1fr}.v33-plan-handoff>div+div{border-left:0;border-top:1px solid #2d4859}}
@media(max-width:620px){.v33-gate-grid,.v33-evidence-map{grid-template-columns:1fr}.v33-evidence-map>div+div{border-left:0;border-top:1px solid #2d4859}}



/* ============================================================
   NEXORA CASE COMMAND BRIEF — non-redundant visual overview
   ============================================================ */
.nx-case-brief-hero{margin:18px 0 22px;padding:28px 30px;border:1px solid #34556c;border-radius:20px;background:radial-gradient(circle at 85% 20%,#153149 0,#0d1b26 36%,#091219 75%);position:relative;overflow:hidden}
.nx-case-brief-hero:after{content:'';position:absolute;inset:auto -80px -120px auto;width:330px;height:330px;border:1px solid #31516a;border-radius:50%;opacity:.28;box-shadow:0 0 0 28px rgba(48,81,106,.07),0 0 0 58px rgba(48,81,106,.045)}
.nx-case-brief-kicker{color:#71b9ed;font-size:.68rem;font-weight:900;letter-spacing:.14em}.nx-case-brief-hero h2{font-size:2rem;line-height:1.15;margin:8px 0 8px;max-width:900px}.nx-case-brief-hero p{color:#9bb0bf;font-size:.92rem;line-height:1.6;max-width:950px;margin:0}.nx-case-question{margin-top:18px;padding:14px 16px;border-left:3px solid #69b8ed;background:#0a151e;max-width:1050px}.nx-case-question span{display:block;color:#6fb6e8;font-size:.6rem;font-weight:900;letter-spacing:.12em}.nx-case-question b{display:block;font-size:.98rem;line-height:1.45;margin-top:4px}
.nx-case-dna{display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin:18px 0 28px}.nx-case-dna-card{padding:18px 18px 16px;border:1px solid #294456;border-radius:15px;background:linear-gradient(145deg,#0d1922,#091118);position:relative;overflow:hidden}.nx-case-dna-card:before{content:'';position:absolute;left:0;top:0;width:38%;height:2px;background:#5ca8da}.nx-case-dna-card span{display:block;color:#7897ab;font-size:.61rem;font-weight:900;letter-spacing:.11em}.nx-case-dna-card b{display:block;font-size:1.75rem;line-height:1;margin-top:10px}.nx-case-dna-card small{display:block;color:#8499a9;font-size:.69rem;line-height:1.4;margin-top:7px}

.nx-case-insight{margin:10px 0 16px;border:1px solid #1d3b4a;border-radius:10px;background:#081720;padding:12px 14px;}
.nx-case-insight-label{font:800 9px ui-monospace,SFMono-Regular,monospace;letter-spacing:.12em;color:#59c6e9;margin-bottom:9px;}
.nx-case-insight-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:8px;}
.nx-case-insight-grid>div{padding:8px 10px;border-left:2px solid #245064;background:rgba(9,28,38,.48);min-height:42px;}
.nx-case-insight-grid b{display:block;font:800 9px ui-monospace,SFMono-Regular,monospace;color:#cfe6ee;letter-spacing:.06em;}
.nx-case-insight-grid span{display:block;margin-top:4px;color:#7895a3;font-size:10px;line-height:1.35;}
@media(max-width:850px){.nx-case-insight-grid{grid-template-columns:1fr;}}
.nx-case-section-head{display:flex;justify-content:space-between;align-items:flex-end;gap:20px;margin:28px 0 12px}.nx-case-section-head .eyebrow{color:#6fb8eb;font-size:.64rem;font-weight:900;letter-spacing:.12em}.nx-case-section-head h3{font-size:1.35rem;margin:5px 0 0}.nx-case-section-head p{color:#8298a9;font-size:.75rem;line-height:1.45;margin:0;max-width:530px;text-align:right}
.nx-case-surface{border:1px solid #2d4758;border-radius:18px;background:#091219;padding:18px 20px 10px}.nx-case-surface-note{padding:9px 11px;margin-top:4px;border-top:1px solid #203846;color:#7e96a7;font-size:.68rem;line-height:1.5}
.nx-compare-lens{display:grid;grid-template-columns:1.3fr .65fr .8fr 1.8fr;gap:8px;margin:12px 0 10px}.nx-compare-lens>div{padding:12px 14px;border:1px solid #243f4e;background:linear-gradient(145deg,#0c1922,#09131a);border-radius:12px}.nx-compare-lens span{display:block;color:#628399;font:900 .53rem ui-monospace,monospace;letter-spacing:.1em}.nx-compare-lens b{display:block;font-size:.8rem;margin-top:5px}.nx-compare-lens small{display:block;color:#718a9c;font-size:.58rem;line-height:1.35;margin-top:3px}.nx-compare-lens .reading{border-color:#315d70;background:linear-gradient(145deg,#0d202d,#09151e)}
.nx-case-domain-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:10px}.nx-domain-card{padding:16px;border:1px solid #294353;border-radius:13px;background:#0c171f;cursor:default;transition:transform .18s ease,border-color .18s ease,background .18s ease}.nx-domain-card:hover{transform:translateY(-2px);border-color:#48728d;background:#0e1b25}.nx-domain-card .tag{color:#70b8e9;font-size:.59rem;font-weight:900;letter-spacing:.1em}.nx-domain-card h4{font-size:.9rem;margin:6px 0}.nx-domain-card .counts{display:flex;gap:15px}.nx-domain-card .counts b{font-size:1.15rem}.nx-domain-card .counts span{display:block;color:#718a9b;font-size:.59rem;text-transform:uppercase;letter-spacing:.06em}.nx-domain-card small{display:block;color:#8398a8;font-size:.67rem;line-height:1.45;margin-top:8px}
.nx-change-lab{display:grid;grid-template-columns:.9fr 1.1fr;gap:14px;margin:18px 0}.nx-change-state,.nx-change-impact{border:1px solid #2d4758;border-radius:18px;background:#09131b;overflow:hidden}.nx-change-state{padding:20px}.nx-change-state .eyebrow,.nx-change-impact .eyebrow{color:#6fb8eb;font-size:.61rem;font-weight:900;letter-spacing:.12em}.nx-change-state h3{font-size:1.25rem;margin:7px 0 4px}.nx-change-state .sub{color:#8da2b2;font-size:.74rem}.nx-algo-swap{display:grid;grid-template-columns:1fr 45px 1fr;align-items:center;margin-top:18px}.nx-algo-box{padding:15px;border:1px solid #2d4a5c;border-radius:12px;background:#0d1a23}.nx-algo-box.target{border-color:#3d6f57;background:#0c1915}.nx-algo-box span{display:block;color:#728da1;font-size:.58rem;font-weight:900;letter-spacing:.1em}.nx-algo-box b{display:block;font-size:1.05rem;margin-top:5px}.nx-algo-box small{display:block;color:#8299a9;font-size:.65rem;margin-top:4px}.nx-swap-arrow{text-align:center;color:#68b8e9;font-size:1.3rem}.nx-impact-head{padding:18px 20px 14px;border-bottom:1px solid #233d4d}.nx-impact-head h3{font-size:1.12rem;margin:6px 0 0}.nx-impact-grid{display:grid;grid-template-columns:repeat(4,1fr)}.nx-impact-grid>div{padding:14px 15px;min-height:82px}.nx-impact-grid>div+div{border-left:1px solid #233b4a}.nx-impact-grid span{display:block;color:#718da1;font-size:.57rem;font-weight:900;letter-spacing:.09em}.nx-impact-grid b{display:block;font-size:1rem;margin-top:5px}.nx-impact-grid small{display:block;color:#8298a8;font-size:.62rem;margin-top:3px}.nx-live-pill-row{display:flex;flex-wrap:wrap;gap:7px;margin-top:14px}.nx-live-pill{padding:6px 9px;border-radius:999px;border:1px solid #31516a;background:#0d1c27;color:#9fc6df;font-size:.61rem;font-weight:800}.nx-live-pill.affected{border-color:#3e7058;background:#0c1915;color:#9ed6b6}.nx-live-empty{padding:17px;border:1px dashed #2d4a5d;border-radius:12px;color:#8298a8;font-size:.72rem;line-height:1.55;background:#091219}
.nx-case-compare{border:1px solid #2d4758;border-radius:18px;background:#091219;padding:18px 20px 8px}.nx-compare-head{display:flex;justify-content:space-between;gap:15px;align-items:center;margin-bottom:5px}.nx-compare-head h3{font-size:1.05rem;margin:0}.nx-compare-head span{color:#7d95a6;font-size:.68rem}.nx-compare-caption{padding:8px 0 2px;color:#7f96a7;font-size:.67rem;line-height:1.5}
.nx-case-journey{display:grid;grid-template-columns:repeat(5,1fr);border:1px solid #2d4758;border-radius:18px;overflow:hidden;background:#091219;margin:18px 0 22px}.nx-journey-step{padding:18px 15px;min-height:120px;background:#0b151d}.nx-journey-step+.nx-journey-step{border-left:1px solid #273f4e}.nx-journey-step.active{background:linear-gradient(145deg,#10273a,#0c1923);box-shadow:inset 0 -3px 0 #5eaee0}.nx-journey-step span{display:block;color:#6faed6;font-size:.58rem;font-weight:900;letter-spacing:.1em}.nx-journey-step b{display:block;font-size:.82rem;margin-top:7px}.nx-journey-step small{display:block;color:#8196a6;font-size:.65rem;line-height:1.45;margin-top:5px}.nx-case-footnote{padding:12px 14px;border-left:3px solid #3e7058;background:#0a1612;color:#8ebaa1;font-size:.67rem;line-height:1.55;margin:16px 0 18px}
@media(max-width:1000px){.nx-compare-lens{grid-template-columns:1fr 1fr}.nx-compare-lens .reading{grid-column:1/-1}.nx-case-dna{grid-template-columns:1fr 1fr}.nx-change-lab{grid-template-columns:1fr}.nx-case-domain-grid{grid-template-columns:1fr 1fr}.nx-impact-grid{grid-template-columns:1fr 1fr}.nx-impact-grid>div:nth-child(3){border-left:0;border-top:1px solid #233b4a}.nx-impact-grid>div:nth-child(4){border-top:1px solid #233b4a}.nx-case-journey{grid-template-columns:1fr 1fr}.nx-journey-step:nth-child(odd){border-left:0}.nx-journey-step:nth-child(n+3){border-top:1px solid #273f4e}}
@media(max-width:650px){.nx-case-dna,.nx-case-domain-grid,.nx-case-journey{grid-template-columns:1fr}.nx-case-section-head{display:block}.nx-case-section-head p{text-align:left;margin-top:6px}.nx-impact-grid{grid-template-columns:1fr}.nx-impact-grid>div{border-left:0!important;border-top:1px solid #233b4a}.nx-impact-grid>div:first-child{border-top:0}.nx-algo-swap{grid-template-columns:1fr}.nx-swap-arrow{padding:8px}.nx-case-brief-hero h2{font-size:1.55rem}}

.v40-assess-answer{display:grid;grid-template-columns:1fr 260px;gap:22px;align-items:stretch;margin:18px 0 20px;border:1px solid #38566d;border-radius:18px;background:linear-gradient(135deg,#112331,#0b141c);overflow:hidden}.v40-assess-answer>div:first-child{padding:25px 28px}.v40-assess-answer span,.v40-section-head>span,.v40-reasoning-chain span,.v40-evidence-card>span,.v40-cmis-hero span,.v40-ai-result span,.v40-model-provenance span,.v40-handoff span{display:block;color:#6eb8ea;font-size:.64rem;font-weight:900;letter-spacing:.13em}.v40-assess-answer h2{font-size:1.75rem;margin:7px 0}.v40-assess-answer p{color:#a9bac8;line-height:1.65;margin:0;max-width:950px}.v40-answer-badge{border-left:1px solid #294255;padding:25px;display:flex;flex-direction:column;justify-content:center;background:#0c1720}.v40-answer-badge b{font-size:1.8rem;margin:5px 0}.v40-answer-badge small{color:#91a6b6;line-height:1.5}.v40-reasoning-chain{border:1px solid #293f50;border-radius:16px;background:#0b141c;margin:20px 0;padding:18px}.v40-chain-head{display:flex;justify-content:space-between;gap:15px;align-items:baseline;margin-bottom:15px}.v40-chain-head span{color:#6eb8ea;font-size:.64rem;font-weight:900;letter-spacing:.13em}.v40-chain-head b{font-size:.93rem}.v40-chain-grid{display:grid;grid-template-columns:repeat(5,1fr);gap:0;border-top:1px solid #253745;border-bottom:1px solid #253745}.v40-chain-grid>div{padding:16px 14px;border-right:1px solid #253745;position:relative}.v40-chain-grid>div:last-child{border-right:0}.v40-chain-grid i{display:inline-flex;width:25px;height:25px;border:1px solid #41637a;border-radius:50%;align-items:center;justify-content:center;font-style:normal;color:#79bdf0;font-size:.65rem;margin-bottom:9px}.v40-chain-grid span{font-size:.57rem}.v40-chain-grid b{display:block;margin-top:5px;font-size:.9rem}.v40-chain-grid small{display:block;color:#8398a9;line-height:1.45;margin-top:5px}.v40-section-head{margin:28px 0 12px}.v40-section-head h3{font-size:1.35rem;margin:5px 0 4px}.v40-section-head p{color:#8fa3b3;line-height:1.55;margin:0;font-size:.82rem}.v40-evidence-card{height:100%;padding:19px;border:1px solid #293f50;border-radius:15px;background:linear-gradient(180deg,#0f1a23,#0b141b)}.v40-evidence-card h3{margin:7px 0 12px;font-size:1.02rem}.v40-mini-row{display:flex;justify-content:space-between;gap:10px;padding:8px 0;border-top:1px solid #223441}.v40-mini-row b{color:#9db0bf;font-size:.78rem;font-weight:650}.v40-mini-row strong{font-size:.8rem}.v40-evidence-card small{display:block;color:#758b9d;line-height:1.5;margin-top:10px}.v40-cmis-hero{display:flex;justify-content:space-between;gap:20px;align-items:flex-end;border:1px solid #39566c;border-radius:15px;padding:20px;background:#0d1922}.v40-cmis-hero b{display:block;font-size:2.3rem;margin-top:3px}.v40-cmis-hero b small{font-size:.9rem;color:#7f98aa}.v40-cmis-hero p{color:#8297a8;font-size:.76rem;margin:5px 0 0}.v40-risk-label{font-size:1.2rem;font-weight:900;text-align:right}.v40-risk-label small{display:block;color:#8195a5;font-size:.68rem;font-weight:500;margin-top:3px}.v40-formula{font-family:Consolas,monospace;border:1px solid #263d4d;background:#081018;border-radius:10px;padding:13px 15px;margin:10px 0;color:#dcebf4;font-size:.88rem}.v40-note{border:1px solid #263d4d;background:#0b151d;border-radius:10px;padding:12px;color:#8ea3b3;font-size:.75rem;line-height:1.55}.v40-ai-result{border:1px solid #35536a;border-radius:12px;background:#0d1922;padding:13px 15px;margin-top:10px}.v40-ai-result b{display:block;font-size:1.1rem;margin-top:4px}.v40-ai-result small{display:block;color:#8ca1b1;margin-top:3px}.v40-model-provenance{display:grid;grid-template-columns:1fr 1fr;border:1px solid #2b4252;border-radius:14px;background:#0b151d;margin:18px 0;padding:0}.v40-model-provenance>div{padding:17px 19px}.v40-model-provenance>div+div{border-left:1px solid #2b4252}.v40-model-provenance b{display:block;font-size:.9rem;margin-top:5px}.v40-model-provenance small{display:block;color:#879cac;line-height:1.5;margin-top:5px}.v40-handoff{display:grid;grid-template-columns:1.1fr .9fr;border:1px solid #3a5d75;border-radius:16px;background:linear-gradient(135deg,#10222f,#0b151d);margin:22px 0;overflow:hidden}.v40-handoff>div{padding:20px}.v40-handoff>div+div{border-left:1px solid #2e485a}.v40-handoff h3{margin:5px 0 7px;font-size:1.18rem}.v40-handoff p,.v40-handoff small{color:#91a5b5;line-height:1.55}.v40-handoff small{display:block;margin-top:7px}
@media(max-width:1050px){.v40-chain-grid{grid-template-columns:1fr 1fr}.v40-chain-grid>div:nth-child(2){border-right:0}.v40-chain-grid>div:nth-child(n+3){border-top:1px solid #253745}.v40-assess-answer{grid-template-columns:1fr}.v40-answer-badge{border-left:0;border-top:1px solid #294255}.v40-model-provenance{grid-template-columns:1fr}.v40-model-provenance>div+div{border-left:0;border-top:1px solid #2b4252}}
.v40-purpose-panel{position:sticky;top:20px;border:1px solid #2e4b5e;border-radius:15px;background:linear-gradient(180deg,#0e1a23,#0b141b);padding:20px}.v40-purpose-panel span,.v40-table-label span{display:block;color:#6eb8ea;font-size:.62rem;font-weight:900;letter-spacing:.13em}.v40-purpose-panel h3{font-size:1.15rem;margin:6px 0 14px}.v40-purpose-panel p{color:#91a6b5;font-size:.78rem;line-height:1.6;margin:0 0 12px}.v40-purpose-panel p b{color:#dce8ef}.v40-purpose-panel strong{display:block;color:#6eb8ea;font-size:.61rem;letter-spacing:.11em;margin-top:16px}.v40-purpose-panel small{display:block;color:#8398a8;line-height:1.5;margin-top:5px}.v40-table-label{margin-bottom:7px}.v40-table-label b{display:block;font-size:.92rem;margin-top:3px}
</style>
""", unsafe_allow_html=True)

STAGES=[
    ("OVERVIEW","OVERVIEW"),
    ("DISCOVERY","INFRASTRUCTURE DISCOVERY"),
    ("ACDKG","ACDKG DEPENDENCY GRAPH"),
    ("RISK","CRYPTO RISK ANALYSIS"),
    ("PLAN","MIGRATION PLANNER"),
    ("SIMULATE","MIGRATION SIMULATION"),
]

def kpis(items):
    cols=st.columns(len(items))
    for c,(label,val) in zip(cols,items):
        with c:
            danger= str(label).lower() in {"high / critical","risk","modeled risk"} and str(val) in {"CRITICAL","HIGH"}
            st.markdown(f"<div class='nx-kpi {'nx-kpi-danger' if danger else ''}'><div class='nx-kpi-label'>{html.escape(str(label))}</div><div class='nx-kpi-value'>{html.escape(str(val))}</div></div>",unsafe_allow_html=True)

def engine_state(stage):
    idx=[x[0] for x in STAGES].index(stage)
    if idx==0: return "CASE LOADED · READY TO DISCOVER"
    if idx==1: return "DISCOVERY ACTIVE · EVIDENCE READY"
    if idx==2: return "DISCOVERY COMPLETE · TRACING RELATIONSHIPS"
    if idx==3: return "ACDKG READY · ASSESSING RISK"
    if idx==4: return "RISK ASSESSMENT READY · GENERATING PLAN"
    return "MIGRATION PLAN READY · SIMULATION AVAILABLE"

def brand(stage=None):
    state=engine_state(stage or st.session_state.get("stage","OVERVIEW"))
    st.markdown(f"<div class='nx-brand-row'><div><div class='nx-brand'>🔐 NEXORA</div><div class='nx-sub'>AI-Driven Crypto-Agility Orchestration Framework</div></div><div class='nx-live'><span class='nx-dot'></span>{html.escape(state)}</div></div>",unsafe_allow_html=True)

def stage_bar(active):
    idx=[s[0] for s in STAGES].index(active); percent=int((idx+1)/len(STAGES)*100)
    bits=[]
    for i,(key,label) in enumerate(STAGES):
        cls="nx-progress-item" + (" active" if i==idx else " done" if i<idx else "")
        bits.append(f"<span class='{cls}'>{i+1:02d} · {label}</span>")
        if i<len(STAGES)-1: bits.append("<span class='nx-progress-arrow'>→</span>")
    st.markdown(f"<div class='nx-progress-wrap'><div class='nx-progress'>{''.join(bits)}</div><div class='nx-progress-meta'><span>Investigation stage <b>{idx+1} of {len(STAGES)}</b></span><span>{percent}% complete</span></div><div class='nx-line'><div class='nx-fill' style='width:{percent}%'></div></div></div>",unsafe_allow_html=True)

def case_banner(name):
    p=SCENARIOS[name]
    status,desc=exposure_summary()
    cls="nx-status-item" + (" nx-card-danger" if status=="CRITICAL EXPOSURE" else "")
    st.markdown(f"<div class='nx-case-head'><div class='nx-case-head-top'><div class='nx-case-name'>{p['icon']} {html.escape(name)} <span class='nx-case-id'>· {p['case']}</span></div><div class='nx-case-id'>{html.escape(p['focus'])}</div></div><div class='nx-case-purpose'>{html.escape(p['summary'])}</div><div class='nx-boundary'>Controlled laboratory case · no production changes</div></div>",unsafe_allow_html=True)
    st.markdown(f"<div class='nx-engine'><span><b>{html.escape(status)}</b> · {html.escape(desc)}</span><span>ACDKG · {len(G.nodes)} nodes / {G.number_of_edges()} relationships</span><span class='nx-engine-state'>● {html.escape(engine_state(st.session_state.stage))}</span></div>",unsafe_allow_html=True)

def asset_label(aid):
    r=df.loc[df.id==aid].iloc[0]; return f"{aid} · {r['name']} · {r['algorithm']}"

def component_cards():
    role_labels={"web":"EDGE / WEB","app":"APPLICATION","api":"SERVICE / API","auth":"IDENTITY / PKI","db":"DATA","vpn":"NETWORK ACCESS","admin":"ADMINISTRATION","ssh":"ADMIN SERVICE","legacy":"LEGACY"}
    p=SCENARIOS[st.session_state.selected_environment]
    cards=[]
    for role in ROLE_KEYS:
        if role in p["roles"]: cards.append((role_labels[role],p["roles"][role]))
    for _,name,typ,status,lib,proto in COMPONENTS.itertuples(index=False):
        if name not in p["roles"].values() and name!={"PKI"}: cards.append((typ.upper(),name))
    cols=st.columns(2)
    for i,(typ,name) in enumerate(cards):
        with cols[i%2]:
            st.markdown(f"<div class='nx-card'><span class='nx-badge'>{html.escape(typ)}</span><h3>{html.escape(name)}</h3><p class='nx-muted'>Modeled infrastructure component · relationship evidence available in ACDKG.</p></div>",unsafe_allow_html=True)

def evidence_grid(row):
    depths=dependency_depths(row.id); tech=technical_dependencies(row.id); f=feature_row(row).iloc[0]
    c1,c2,c3=st.columns(3)
    with c1: st.markdown(f"<div class='nx-evidence'><b>DEPENDENCY EVIDENCE</b><br>Owner: <b>{html.escape(str(row.owner))}</b><br>Depth: <b>{max(depths.values(),default=0)}</b><br>Operational dependents: <b>{max(len(depths)-1,0)}</b><br>Affected components: <b>{len(impacted_components(row.id))}</b></div>",unsafe_allow_html=True)
    with c2: st.markdown(f"<div class='nx-evidence'><b>CRYPTOGRAPHIC EVIDENCE</b><br>Algorithm: <b>{row.algorithm}</b><br>Role: <b>{row.crypto_role}</b><br>Protocol: <b>{row.protocol}</b><br>PQC direction: <b>{row['Suggested PQC']}</b></div>",unsafe_allow_html=True)
    with c3: st.markdown(f"<div class='nx-evidence'><b>MODEL EVIDENCE</b><br>Criticality: <b>{int(f['criticality'])}/5</b><br>Exposure: <b>{int(f['exposure'])}/5</b><br>Complexity: <b>{int(f['complexity'])}/5</b><br>AI effort: <b>{row['ML Effort']}</b></div>",unsafe_allow_html=True)

def graph_figure(asset_id, full=False):
    row=df.loc[df.id==asset_id].iloc[0]
    if full:
        sub=G.copy()
    else:
        affected=set(impacted_components(asset_id))
        technical={n for n,_ in technical_dependencies(asset_id)}
        sub=G.subgraph(affected|{asset_id}|technical).copy()
    if sub.number_of_nodes()==0:
        return go.Figure()
    pos=nx.spring_layout(sub,seed=42,k=1.45)
    symbols={
        "Network":"circle","Service":"square","Application":"diamond",
        "Network Device":"hexagon","Endpoint":"triangle-up","Protocol":"pentagon",
        "Library":"star","Security Service":"cross","Crypto Asset":"x",
        "Crypto Algorithm":"circle","Component":"circle"
    }
    colors={
        "Crypto Asset":"#71b8ff","Crypto Algorithm":"#a987ff","Library":"#f1c76b",
        "Security Service":"#64d29b","Service":"#5ea7df","Application":"#d98bba",
        "Network":"#7c8ea4","Network Device":"#7c8ea4","Endpoint":"#9aa8b6",
        "Protocol":"#c58f62","Component":"#6f8297"
    }
    edge_x=[];edge_y=[]
    for a,b,d in sub.edges(data=True):
        x0,y0=pos[a];x1,y1=pos[b]
        edge_x += [x0,x1,None];edge_y += [y0,y1,None]
    traces=[go.Scatter(x=edge_x,y=edge_y,mode="lines",line=dict(width=1.5,color="#435365"),hoverinfo="none",showlegend=False)]
    grouped={}
    for n in sub.nodes():
        typ=sub.nodes[n].get("node_type","Component")
        grouped.setdefault(typ,[]).append(n)
    for typ,nodes in grouped.items():
        xs=[];ys=[];texts=[];hovers=[];sizes=[];symbols_list=[];line_width=[]
        for n in nodes:
            x,y=pos[n];xs.append(x);ys.append(y);texts.append(n)
            hovers.append(f"{html.escape(str(n))}<br>Type: {html.escape(str(typ))}")
            sizes.append(31 if n==asset_id else 17)
            symbols_list.append(symbols.get(typ,"circle"))
            line_width.append(2.2 if n==asset_id else 1)
        traces.append(go.Scatter(
            x=xs,y=ys,mode="markers+text",text=texts,textposition="top center",
            hovertext=hovers,hoverinfo="text",name=typ,
            marker=dict(size=sizes,symbol=symbols_list,color=colors.get(typ,"#7c8ea4"),line=dict(width=line_width,color="#0b1118"))
        ))
    fig=go.Figure(traces)
    fig.update_layout(
        height=560 if full else 500,
        margin=dict(l=15,r=15,t=15,b=15),showlegend=True,
        legend=dict(orientation="h",yanchor="bottom",y=1.01,xanchor="left",x=0,
                    bgcolor="rgba(0,0,0,0)",font=dict(size=10,color="#aebdcb")),
        paper_bgcolor="#0c1219",plot_bgcolor="#0c1219",
        xaxis=dict(visible=False),yaxis=dict(visible=False),
        font=dict(color="#dce5ee")
    )
    return fig

def phase_roadmap(selected_id):
    row=df.loc[df.id==selected_id].iloc[0]
    phases=[
        ("01","INVENTORY VALIDATION","Confirm vulnerable algorithms, assets and dependency evidence."),
        ("02","PKI PREPARATION","Prepare replacement certificates / key material and authentication dependencies."),
        ("03","HIGH-IMPACT SERVICE MIGRATION",f"Prepare the selected {row['name']} for controlled migration."),
        ("04","APPLICATION MIGRATION","Update applications and services that depend on the migrated cryptographic component."),
        ("05","VALIDATION","Verify connectivity, authentication and dependency integrity; update inventory."),
    ]
    st.markdown("<div class='nx-roadmap'>"+"".join([f"<div class='nx-road-node {'active' if i==2 else ''}'><div class='n'>{num}</div><h3>{html.escape(title)}</h3><p>{html.escape(desc)}</p></div>" + ("<div class='nx-road-arrow'>→</div>" if i<len(phases)-1 else "") for i,(num,title,desc) in enumerate(phases)])+"</div>",unsafe_allow_html=True)

def risk_card(level,title,text):
    cls="nx-finding critical" if level in {"CRITICAL","HIGH"} else "nx-finding"
    st.markdown(f"<div class='{cls}'><div class='nx-finding-title'>{html.escape(title)}</div><h2>{html.escape(level)}</h2><p>{text}</p></div>",unsafe_allow_html=True)

def current_stage_idx(): return [x[0] for x in STAGES].index(st.session_state.stage)

def go_stage(key):
    st.session_state.visited_stages.add(key)
    st.session_state.stage=key
    st.session_state["_reset_page_scroll"]=True
    st.rerun()


# Compatibility shim retained only for older generated references; current navigation uses reset_page_scroll_if_needed directly.
def v28_stage_scroll_reset():
    st.markdown("""<script>window.parent.scrollTo({top:0,left:0,behavior:'instant'});document.documentElement.scrollTop=0;document.body.scrollTop=0;</script>""", unsafe_allow_html=True)

def reset_page_scroll_if_needed():
    if st.session_state.pop("_reset_page_scroll", False):
        # One generic reset mechanism. It uses the same parent-document technique that
        # Streamlit navigation needs, but is defined before the first stage render.
        components.html("""<script>
        (function(){
          function reset(){
            try{
              const p=window.parent;
              ['section.main','[data-testid=\"stAppViewContainer\"]','[data-testid=\"stAppViewBlockContainer\"]'].forEach(function(sel){
                try{const el=p.document.querySelector(sel);if(el){el.scrollTop=0;}}catch(e){}
              });
              try{p.document.documentElement.scrollTop=0;}catch(e){}
              try{p.document.body.scrollTop=0;}catch(e){}
              try{p.scrollTo(0,0);}catch(e){}
            }catch(e){}
          }
          reset();setTimeout(reset,80);setTimeout(reset,220);setTimeout(reset,500);
        })();
        </script>""",height=1)

# ============================================================
# PRESENTATION HELPERS — dynamic case intelligence
# ============================================================

def preview_case_metrics(name):
    tdf, tg, tcomp = build_scenario_data(name)
    records=[]
    for _, r in tdf.iterrows():
        owners=[s for s,t,d in tg.edges(data=True) if t==r.id and d.get("relation")=="protected_by"]
        depths={}
        q=[]
        for owner in owners:
            depths[owner]=0;q.append(owner)
        while q:
            cur=q.pop(0)
            for pred in tg.predecessors(cur):
                if tg.edges[pred,cur].get("relation")!="depends_on":
                    continue
                nd=depths[cur]+1
                if pred not in depths or nd<depths[pred]:
                    depths[pred]=nd;q.append(pred)
        affected=max(len(depths),0)
        dependency_factor=min(max(affected-1,0),5)
        vuln=ALGORITHM_VULNERABILITY.get(r["algorithm"],2)
        cmis=min(round(vuln*8+r["criticality"]*6+r["exposure"]*5+r["complexity"]*4+dependency_factor*3),100)
        records.append((cmis,r["id"],r["name"],r["algorithm"],affected))
    records.sort(reverse=True)
    top=records[0]
    return {"components":len(tcomp),"assets":len(tdf),"relationships":tg.number_of_edges(),"top":top,"critical":sum(1 for x in records if x[0]>=81),"high":sum(1 for x in records if 61<=x[0]<=80)}

def activity_feed(stage):
    trace_id=st.session_state.get("trace_asset")
    row=df.loc[df.id==trace_id].iloc[0] if trace_id in df.id.tolist() else None
    affected=len(impacted_components(row.id)) if row is not None else 0
    actions={
        "OVERVIEW":[
            f"Loaded case model: {SCENARIOS[st.session_state.selected_environment]['case']}.",
            f"Prepared {len(COMPONENTS)} modeled infrastructure components.",
            f"Identified {len(df)} cryptographic assets for investigation.",
        ],
        "DISCOVERY":[
            f"Enumerating {len(COMPONENTS)} modeled infrastructure components.",
            f"Classifying {len(df)} cryptographic assets by role, owner and protocol.",
            "Evidence boundary established: controlled case model + optional local host evidence.",
        ],
        "ACDKG":[
            f"Constructed directed ACDKG with {len(G.nodes)} nodes and {G.number_of_edges()} relationships.",
            f"Tracing operational predecessors for {row.id} · {row['name']}." if row is not None else "No investigation target selected yet; discovery evidence is being established.",
            f"Current trace contains {affected} affected component(s).",
        ],
        "RISK":[
            "Combining cryptographic vulnerability with dependency and infrastructure attributes.",
            f"Calculated CMIS for {len(df)} assets; {int(df.Risk.isin(['HIGH','CRITICAL']).sum())} are HIGH/CRITICAL.",
            f"Controlled Random Forest produced an effort estimate for {row.id}.",
        ],
        "PLAN":[
            "Ranking assets using CMIS, dependency depth, downstream dependents and AI effort.",
            f"Building preparation and validation gates for {row.id}.",
            "Generating the five documented migration phases.",
        ],
        "SIMULATE":[
            f"Loaded proposed transition for {row.id} · {row.algorithm}.",
            f"Checking role compatibility and {affected} modeled affected component(s).",
            "Preparing consequence paths and deployment validation gates.",
        ],
    }
    return actions.get(stage,[])

def render_activity_feed(stage):
    rows=activity_feed(stage)
    st.markdown("<div class='nx-activity'>"+''.join(
        f"<div class='nx-activity-row'><span class='nx-activity-dot'></span><span class='nx-activity-text'>{html.escape(x)}</span></div>" for x in rows
    )+"</div>",unsafe_allow_html=True)

# ============================================================
# V32 USER CONTROL + VISUAL PROOF
# ============================================================
def set_investigation_asset(asset_id):
    if asset_id not in df.id.tolist(): return
    previous=st.session_state.get("trace_asset")
    st.session_state.trace_asset=asset_id
    st.session_state.discovery_asset=asset_id
    st.session_state.simulation_asset=asset_id
    if previous != asset_id:
        st.session_state.pqc_target=None
        st.session_state.simulation_result=None


def render_investigation_controls():
    current=st.session_state.get("trace_asset"); ids=df.id.tolist()
    labels={r.id:f"{r.id} · {r['name']} · {r.algorithm}" for _,r in df.iterrows()}
    opts=["Select an investigation asset…"]+ids
    idx=ids.index(current)+1 if current in ids else 0
    st.markdown("<div class='v32-control-wrap'><div class='v32-control-head'><div><span>INVESTIGATION CONTROLS</span><b>You choose the asset. NEXORA recalculates the downstream evidence.</b></div><small>Available on every stage</small></div>",unsafe_allow_html=True)
    c1,c2,c3=st.columns([1.45,1.05,.55],gap="medium")
    with c1:
        picked=st.selectbox("Cryptographic asset",opts,index=idx,format_func=lambda x: "Select an investigation asset…" if x==opts[0] else labels.get(x,x),key="v32_global_asset")
        if picked!=opts[0] and picked!=current:
            set_investigation_asset(picked); st.rerun()
    current=st.session_state.get("trace_asset")
    row=df.loc[df.id==current].iloc[0] if current in ids else None
    with c2:
        target_opts=["Select a PQC target…"]+(PQC_OPTIONS.get(row.crypto_role,[]) if row is not None else [])
        tc=st.session_state.get("pqc_target"); ti=target_opts.index(tc) if tc in target_opts else 0
        target=st.selectbox("Proposed PQC direction",target_opts,index=ti,key="v32_global_target",disabled=row is None)
        if row is not None: st.session_state.pqc_target=None if target==target_opts[0] else target
    with c3:
        st.markdown("<div class='v32-control-status'><span>ACTIVE</span><b>"+(html.escape(str(current)) if current in ids else "—")+"</b><small>"+(html.escape(str(st.session_state.get('pqc_target'))) if st.session_state.get('pqc_target') else "PQC target not set")+"</small></div>",unsafe_allow_html=True)
    st.markdown("</div>",unsafe_allow_html=True)


def infrastructure_crypto_bridge_figure(selected_asset=None):
    fig=go.Figure(); comps=list(COMPONENTS.iloc[:,1].astype(str)); assets=list(df.id.astype(str))
    if not comps or not assets: return fig
    cy=np.linspace(1,0,len(comps)) if len(comps)>1 else [0.5]; ay=np.linspace(1,0,len(assets)) if len(assets)>1 else [0.5]
    cp={c:float(y) for c,y in zip(comps,cy)}; ap={a:float(y) for a,y in zip(assets,ay)}
    for _,r in df.iterrows():
        owner=str(r.owner); aid=str(r.id)
        if owner in cp:
            fig.add_trace(go.Scatter(x=[.12,.88],y=[cp[owner],ap[aid]],mode='lines',line=dict(width=4 if aid==selected_asset else 1.4),hoverinfo='skip',showlegend=False))
    fig.add_trace(go.Scatter(x=[.12]*len(comps),y=cy,mode='markers+text',text=comps,textposition='middle right',marker=dict(size=10),hovertemplate='%{text}<extra>Infrastructure</extra>',showlegend=False))
    fig.add_trace(go.Scatter(x=[.88]*len(assets),y=ay,mode='markers+text',text=assets,textposition='middle left',marker=dict(size=[15 if a==selected_asset else 9 for a in assets]),hovertext=df['name'],hovertemplate='%{hovertext}<extra>Crypto asset</extra>',showlegend=False))
    fig.update_layout(height=max(300,min(520,170+30*max(len(comps),len(assets)))),margin=dict(l=10,r=10,t=10,b=10),paper_bgcolor='#0b1219',plot_bgcolor='#0b1219',font=dict(color='#dce8f1'),xaxis=dict(range=[0,1],visible=False),yaxis=dict(range=[-.08,1.08],visible=False),showlegend=False)
    return fig


def plan_level_figure(level,row):
    """Readable engineering diagrams with deliberately separated nodes.
    The content remains asset-specific; only the layout is changed to avoid congestion.
    """
    current=str(row.algorithm); target=str(row['Suggested PQC'])
    owner=str(row.owner); protocol=str(row.protocol)

    if level==0:
        nodes=[
            "1 · UNDERSTAND<br><span style='font-size:11px'>Identify asset + what it protects</span>",
            "2 · PREPARE<br><span style='font-size:11px'>Check dependencies + replacement</span>",
            "3 · VALIDATE<br><span style='font-size:11px'>Test compatibility before change</span>",
            "4 · CHANGE<br><span style='font-size:11px'>Apply only in a controlled step</span>",
            "5 · VERIFY<br><span style='font-size:11px'>Confirm service + inventory state</span>"
        ]
        coords=[(.50,.90),(.50,.70),(.50,.50),(.50,.30),(.50,.10)]
        edges=[(0,1),(1,2),(2,3),(3,4)]
        height=520
        font_size=14
    elif level==1:
        nodes=[
            f"ASSET<br><span style='font-size:11px'>{html.escape(str(row.id))} · {html.escape(current)}</span>",
            f"PKI / CERTIFICATE<br><span style='font-size:11px'>{html.escape(target)}</span>",
            f"PROTOCOL<br><span style='font-size:11px'>{html.escape(protocol)}</span>",
            f"OWNER / SERVICE<br><span style='font-size:11px'>{html.escape(owner)}</span>",
            "CONTROLLED VALIDATION<br><span style='font-size:11px'>Compatibility + continuity checks</span>",
            "GO / HOLD<br><span style='font-size:11px'>Proceed only with evidence</span>"
        ]
        coords=[(.18,.78),(.50,.78),(.82,.78),(.18,.28),(.50,.28),(.82,.28)]
        edges=[(0,1),(1,2),(0,3),(1,4),(2,4),(3,4),(4,5)]
        height=450
        font_size=13
    else:
        nodes=[
            f"1 · SELECT ASSET<br><span style='font-size:10px'>{html.escape(str(row.id))} · {html.escape(current)}</span>",
            "2 · CRYPTO PROVIDER<br><span style='font-size:10px'>Library / implementation</span>",
            "3 · KEY + CERTIFICATE<br><span style='font-size:10px'>Material + trust chain</span>",
            f"4 · PROTOCOL CONFIG<br><span style='font-size:10px'>{html.escape(protocol)}</span>",
            "5 · DEPENDENT SERVICES<br><span style='font-size:10px'>Applications / services</span>",
            "6 · LIBRARY TEST<br><span style='font-size:10px'>Algorithm/provider support</span>",
            "7 · TRUST TEST<br><span style='font-size:10px'>Certificate + identity</span>",
            "8 · CONTINUITY TEST<br><span style='font-size:10px'>Application/service</span>",
            "9 · ROLLBACK CHECKPOINT<br><span style='font-size:10px'>Ready before change</span>",
            f"10 · CONTROLLED CHANGE<br><span style='font-size:10px'>{html.escape(target)}</span>",
            "11 · POST-CHANGE EVIDENCE<br><span style='font-size:10px'>Inventory + configuration</span>"
        ]
        # Deliberate 4 / 4 / 3 layout: enough room for text and arrows.
        coords=[
            (.14,.86),(.38,.86),(.62,.86),(.86,.86),
            (.14,.55),(.38,.55),(.62,.55),(.86,.55),
            (.26,.18),(.56,.18),(.82,.18)
        ]
        edges=[(0,1),(0,2),(2,6),(3,4),(1,5),(4,7),(5,9),(6,9),(7,9),(9,10),(9,8),(8,10)]
        height=610
        font_size=12

    fig=go.Figure()
    for a,b in edges:
        fig.add_annotation(
            x=coords[b][0],y=coords[b][1],ax=coords[a][0],ay=coords[a][1],
            xref='x',yref='y',axref='x',ayref='y',text='',showarrow=True,
            arrowhead=3,arrowsize=1.0,arrowwidth=1.8,arrowcolor='#5c91b4'
        )
    for idx,(x,y) in enumerate(coords):
        fig.add_annotation(
            x=x,y=y,text=nodes[idx],showarrow=False,xanchor='center',yanchor='middle',
            align='center',
            bgcolor='#102231' if idx==0 else '#0c1821',
            bordercolor='#5c91b4' if idx in {0,len(nodes)-1} else '#34566b',
            borderwidth=1.5,borderpad=9,
            font=dict(size=font_size,color='#e7f1f6')
        )
    fig.update_layout(
        height=height,margin=dict(l=35,r=35,t=24,b=24),
        paper_bgcolor='#0b1219',plot_bgcolor='#0b1219',
        font=dict(color='#e1edf4'),
        xaxis=dict(range=[0,1],visible=False),
        yaxis=dict(range=[0,1.03],visible=False),
        showlegend=False
    )
    return fig

def live_ai_whatif(row,base_features):
    st.markdown("<div class='v32-ai-lab'><div class='v32-ai-lab-head'><span>NEXORA AI WHAT-IF · EXECUTION PROOF</span><b>Move an input → Streamlit reruns the trained Random Forest → class probabilities and CMIS are recalculated.</b><small>This is a controlled demonstration. It changes only the feature vector used for inference; it does not modify the case dataset or perform a real migration.</small></div>",unsafe_allow_html=True)
    base_vals={k:int(base_features[k]) for k in ML_FEATURES}
    baseline_x=pd.DataFrame([base_vals])[ML_FEATURES]; baseline_pred=MODEL.predict(baseline_x)[0]; baseline_probs=MODEL.predict_proba(baseline_x)[0]
    vals=dict(base_vals); cols=st.columns(4,gap='medium')
    for i,k in enumerate(ML_FEATURES):
        with cols[i%4]:
            lo=0 if k in {'dependency_depth','operational_dependents','technical_dependencies'} else 1; hi=4 if k in {'dependency_depth','operational_dependents','technical_dependencies'} else 5
            vals[k]=st.slider(k.replace('_',' ').title(),lo,hi,base_vals[k],key=f'v33_ai_{k}_{row.id}')
    if st.button("↺ Reset inputs to selected-asset evidence",key=f'v33_ai_reset_{row.id}'):
        for k,v in base_vals.items(): st.session_state[f'v33_ai_{k}_{row.id}']=v
        st.rerun()
    x=pd.DataFrame([vals])[ML_FEATURES]; pred=MODEL.predict(x)[0]; probs=MODEL.predict_proba(x)[0]; conf=float(max(probs))*100
    dep_factor=min(max(vals['dependency_depth']+vals['operational_dependents']-1,0),5)
    cmis=min(round(vals['vulnerability']*8+vals['criticality']*6+vals['exposure']*5+vals['complexity']*4+dep_factor*3),100)
    changed=[k.replace('_',' ') for k in ML_FEATURES if vals[k]!=base_vals[k]]
    delta_conf=(conf-float(max(baseline_probs))*100)
    st.markdown(f"<div class='v33-ai-proofline'><div><span>ALGORITHM EXECUTED</span><b>RandomForestClassifier</b><small>scikit-learn · 220 trees · 7 features</small></div><div><span>LIVE MODEL CALL</span><b>predict_proba()</b><small>Current vector is evaluated on every interaction</small></div><div><span>INPUT CHANGE</span><b>{len(changed)} feature(s)</b><small>{html.escape(', '.join(changed) if changed else 'Move a slider to create a what-if')}</small></div><div><span>OUTPUT DELTA</span><b>{delta_conf:+.1f} pp</b><small>top-class probability vs selected-asset baseline</small></div></div>",unsafe_allow_html=True)
    st.markdown(f"<div class='v32-ai-proof'><div><span>MODEL INPUT</span><b>{len(ML_FEATURES)} editable features</b><small>Numeric feature vector → Random Forest</small></div><div><span>RF OUTPUT</span><b>{html.escape(str(pred))}</b><small>{conf:.1f}% top-class probability · baseline {html.escape(str(baseline_pred))}</small></div><div><span>WHAT-IF CMIS</span><b>{cmis}/100</b><small>{risk_level(cmis)} modeled band · D={dep_factor}</small></div></div>",unsafe_allow_html=True)
    c1,c2=st.columns(2,gap='large')
    with c1:
        d=pd.DataFrame({'Class':MODEL.classes_,'Probability':probs}); fig=go.Figure(go.Bar(x=d.Probability,y=d.Class,orientation='h',text=[f'{v:.1%}' for v in d.Probability],textposition='auto')); fig.update_layout(height=280,margin=dict(l=10,r=20,t=10,b=25),paper_bgcolor='#0b1219',plot_bgcolor='#0b1219',font=dict(color='#dce8f1'),xaxis=dict(range=[0,1],tickformat='.0%',gridcolor='#243947'),yaxis=dict(gridcolor='#243947'),showlegend=False); st.plotly_chart(fig,width='stretch',config={'displayModeBar':False})
    with c2:
        contrib=[('Vulnerability',vals['vulnerability']*8),('Criticality',vals['criticality']*6),('Exposure',vals['exposure']*5),('Complexity',vals['complexity']*4),('Dependency impact',dep_factor*3)]; fig2=go.Figure(go.Bar(x=[v for _,v in contrib],y=[k for k,_ in contrib],orientation='h',text=[str(v) for _,v in contrib],textposition='auto')); fig2.update_layout(height=280,margin=dict(l=10,r=20,t=10,b=25),paper_bgcolor='#0b1219',plot_bgcolor='#0b1219',font=dict(color='#dce8f1'),xaxis=dict(title='CMIS contribution',gridcolor='#243947'),yaxis=dict(gridcolor='#243947'),showlegend=False); st.plotly_chart(fig2,width='stretch',config={'displayModeBar':False})
    st.markdown("</div>",unsafe_allow_html=True)
# ============================================================
def render_technical_overview():
    st.markdown("""<div class='v33-tech-overview'>
      <div class='v33-tech-head'><div><span>TECHNICAL OVERVIEW</span><h3>Where the intelligence actually runs</h3></div><small>Implementation facts · not marketing labels</small></div>
      <div class='v33-tech-grid'>
        <div><span>DEPENDENCY ENGINE</span><b>NetworkX directed graph</b><p>ACDKG relationships are traversed with a breadth-first dependency search to calculate impact depth and consequence paths.</p></div>
        <div><span>AI MODEL</span><b>Random Forest Classifier</b><p>scikit-learn model · 220 trees · max depth 10 · trained on controlled synthetic scenarios.</p></div>
        <div><span>AI INPUT</span><b>7 derived features</b><p>Criticality, exposure, complexity, dependency depth, operational dependents, technical dependencies and vulnerability.</p></div>
        <div><span>DECISION METRIC</span><b>CMIS</b><p>Project-specific weighted calculation. The AI effort signal and CMIS are separate evidence streams.</p></div>
      </div>
      <div class='v33-stack'><span>PROTOTYPE STACK</span><b>Python · Streamlit · Pandas · NetworkX · Plotly · scikit-learn · psutil</b></div>
    </div>""",unsafe_allow_html=True)


st.markdown('<style>\n.v29-evidence-purpose{display:grid;grid-template-columns:1.45fr .55fr;gap:0;margin:20px 0 24px;border:1px solid #304b61;border-radius:16px;overflow:hidden;background:linear-gradient(145deg,#0f1c27,#0a131b)}\n.v29-evidence-purpose>div:first-child{padding:24px 26px}.v29-evidence-purpose span{display:block;color:#70b9ee;font-size:.74rem;font-weight:900;letter-spacing:.13em}.v29-evidence-purpose h3{font-size:1.35rem;margin:8px 0 10px;color:#edf5fa}.v29-evidence-purpose p{font-size:.96rem;line-height:1.72;color:#a8bbc9;margin:0;max-width:900px}.v29-evidence-scope{border-left:1px solid #2d4558;padding:24px 22px;display:flex;flex-direction:column;justify-content:center;background:#0b151e}.v29-evidence-scope b{font-size:.7rem;letter-spacing:.13em;color:#70b9ee}.v29-evidence-scope strong{font-size:1.08rem;color:#edf5fa;margin-top:6px}.v29-evidence-scope small{font-size:.82rem;line-height:1.55;color:#91a7b7;margin-top:7px}\n@media(max-width:900px){.v29-evidence-purpose{grid-template-columns:1fr}.v29-evidence-scope{border-left:0;border-top:1px solid #2d4558}}\n</style>',unsafe_allow_html=True)

# SESSION STATE
# ============================================================
defaults={"selected_environment":None,"analysis_complete":False,"stage":"OVERVIEW","visited_stages":{"OVERVIEW"},"case_seed_asset":None,"trace_asset":None,"simulation_asset":None,"simulation_result":None,"local_evidence":None,"case_preview":None,"discovery_asset":None,"infrastructure_asset":None,"pqc_target":None,"runtime_probe_error":None}
for k,v in defaults.items():
    if k not in st.session_state: st.session_state[k]=v

def activate(name):
    global df,G,COMPONENTS
    df,G,COMPONENTS=build_scenario_data(name);enrich()
    st.session_state.selected_environment=name;st.session_state.analysis_complete=True;st.session_state.stage="OVERVIEW";st.session_state.visited_stages={"OVERVIEW"};st.session_state.case_preview=None
    top=build_plan().iloc[0]["id"]
    # The controlled case retains a reproducible seed internally, but the user has not selected an investigation target yet.
    st.session_state.case_seed_asset=top
    st.session_state.trace_asset=None
    st.session_state.simulation_asset=None
    st.session_state.discovery_asset=None
    st.session_state.infrastructure_asset=None
    st.session_state.simulation_result=None
    st.session_state.local_evidence=None
    st.session_state.pqc_target=None
    st.session_state.runtime_probe_error=None


# ============================================================
# NEXORA V21 — V20 REFINEMENT + EXPLANATION / DECISION CLARITY
# ============================================================

# Additional presentation helpers for V18
def stage_label(key):
    return {
        "OVERVIEW":"CASE",
        "DISCOVERY":"DISCOVER",
        "ACDKG":"TRACE",
        "RISK":"ASSESS",
        "PLAN":"PLAN",
        "SIMULATE":"SIMULATE",
    }.get(key,key)

def stage_question(key):
    return {
        "OVERVIEW":"Why are we investigating this environment?",
        "DISCOVERY":"What exists before we change anything?",
        "ACDKG":"What depends on this cryptographic asset?",
        "RISK":"Why does this dependency matter?",
        "PLAN":"What must happen before the cryptographic change?",
        "SIMULATE":"What happens if the dependency changes?",
    }.get(key,"")

def stage_source(key):
    return {
        "OVERVIEW":"Case model",
        "DISCOVERY":"Case infrastructure + cryptographic inventory",
        "ACDKG":"ACDKG dependency graph",
        "RISK":"ACDKG + CMIS + controlled AI signal",
        "PLAN":"Dependency + risk evidence",
        "SIMULATE":"Dependency + migration model",
    }.get(key,"")

def render_stage_nav(active):
    st.markdown("<div class='v18-ribbon-label'>INVESTIGATION</div>", unsafe_allow_html=True)
    cols = st.columns([1,1.05,1,1,1,1], gap="small")
    for col,(key,label) in zip(cols, STAGES):
        with col:
            active_cls = " v18-nav-active" if key == active else ""
            if st.button(
                f"{STAGES.index((key,label))+1:02d}  {stage_label(key)}",
                key=f"v18_nav_{key}",
                width="stretch",
                type="primary" if key == active else "secondary",
            ):
                if key != st.session_state.stage:
                    go_stage(key)

def render_header():
    p = SCENARIOS[st.session_state.selected_environment]
    st.markdown(
        f"""
        <div class='v18-header'>
          <div>
            <div class='v18-brand'>NEXORA</div>
            <div class='v18-product'>CRYPTO-AGILITY INVESTIGATION CONSOLE</div>
          </div>
          <div class='v18-header-case'>
            <div class='v18-case-id'>{html.escape(p['case'])} · CONTROLLED LAB</div>
            <div class='v18-case-name'>{html.escape(st.session_state.selected_environment)}</div>
            <div class='v18-case-focus'>{html.escape(p['focus'])}</div>
          </div>
        </div>
        """, unsafe_allow_html=True)

def render_context_line():
    p = SCENARIOS[st.session_state.selected_environment]
    trace_id=st.session_state.get("trace_asset")
    if trace_id in df.id.tolist():
        row = df.loc[df.id == trace_id].iloc[0]
        focus=f"INVESTIGATION TARGET · {html.escape(str(row.id))} · {html.escape(str(row['name']))}"
    else:
        focus="INVESTIGATION TARGET · NOT SELECTED — choose an asset in DISCOVER"
    st.markdown(
        f"""
        <div class='v18-context'>
          <div><span class='v18-context-label'>ACTIVE CASE</span><b>{html.escape(p['case'])}</b> · {html.escape(st.session_state.selected_environment)}</div>
          <div class='v18-context-right'>
            <span>{len(COMPONENTS)} components</span>
            <span>{len(df)} crypto assets</span>
            <span>{G.number_of_edges()} ACDKG links</span>
            <span class='v18-context-asset'>{focus}</span>
          </div>
        </div>
        """, unsafe_allow_html=True)

def render_page_intro(number, eyebrow, title, subtitle):
    st.markdown(
        f"""
        <div class='v18-page-intro'>
          <div class='v18-eyebrow'>{number} · {html.escape(eyebrow)}</div>
          <h1>{html.escape(title)}</h1>
          <p>{subtitle}</p>
        </div>
        """, unsafe_allow_html=True)

def render_read_panel(question, evidence, output):
    st.markdown(
        f"""
        <div class='v18-read-panel'>
          <div class='v18-read-head'>HOW TO READ THIS PAGE</div>
          <div class='v18-read-question'>{html.escape(question)}</div>
          <div class='v18-read-row'><span>EVIDENCE</span><b>{html.escape(evidence)}</b></div>
          <div class='v18-read-row'><span>OUTPUT</span><b>{html.escape(output)}</b></div>
        </div>
        """, unsafe_allow_html=True)

def render_asset_hero(row, compact=False):
    risk = str(row["Risk"])
    risk_cls = "critical" if risk in {"CRITICAL","HIGH"} else "warning" if risk == "MODERATE" else "normal"
    affected = len(impacted_components(row.id))
    depth = max(dependency_depths(row.id).values(), default=0)
    st.markdown(
        f"""
        <div class='v18-asset-hero {risk_cls}'>
          <div class='v18-asset-top'>
            <div>
              <div class='v18-eyebrow'>SELECTED CRYPTOGRAPHIC ASSET</div>
              <div class='v18-asset-id'>{html.escape(str(row.id))}</div>
              <h2>{html.escape(str(row['name']))}</h2>
            </div>
            <div class='v18-risk-pill'>{html.escape(risk)}</div>
          </div>
          <div class='v18-asset-meta'>
            <div><span>CURRENT</span><b>{html.escape(str(row.algorithm))}</b></div>
            <div><span>CRYPTO ROLE</span><b>{html.escape(str(row.crypto_role))}</b></div>
            <div><span>OWNER</span><b>{html.escape(str(row.owner))}</b></div>
            <div><span>PROTOCOL</span><b>{html.escape(str(row.protocol))}</b></div>
          </div>
          <div class='v18-asset-stats'>
            <div><b>{int(row.CMIS)}</b><span>CMIS</span></div>
            <div><b>{affected}</b><span>AFFECTED COMPONENTS</span></div>
            <div><b>{depth}</b><span>MAX DEPENDENCY DEPTH</span></div>
            <div><b>{html.escape(str(row['Suggested PQC']))}</b><span>PQC DIRECTION</span></div>
          </div>
        </div>
        """, unsafe_allow_html=True)

def render_home_quote():
    st.markdown(
        """
        <div class='v18-source-band'>
          <div class='v18-source-main'>
            <div class='v18-eyebrow'>WHY THIS PROBLEM IS REAL</div>
            <h2>Crypto agility is an operational migration problem.</h2>
            <p>NIST defines crypto agility around replacing or adapting cryptographic algorithms while preserving security and ongoing operations.</p>
          </div>
          <div class='v18-quote'>
            <div class='v18-quote-mark'>“</div>
            <div class='v18-quote-text'>while preserving security and ongoing operations.</div>
            <div class='v18-quote-source'>NIST · CSWP 39upd1 · 2026</div>
          </div>
        </div>
        <div class='v18-source-links'>
          <a href='https://csrc.nist.gov/pubs/cswp/39/upd1/considerations-for-achieving-crypto-agility/final' target='_blank'>NIST Crypto Agility guidance ↗</a>
          <a href='https://www.nist.gov/cybersecurity-and-privacy/what-post-quantum-cryptography' target='_blank'>NIST PQC guidance ↗</a>
          <a href='https://pages.nist.gov/nccoe-migration-post-quantum-cryptography/' target='_blank'>NIST NCCoE migration project ↗</a>
        </div>
        """, unsafe_allow_html=True)

def render_case_card(name):
    pcase = SCENARIOS[name]
    m = preview_case_metrics(name)
    top = m["top"]
    severity = "CRITICAL" if top[0] >= 81 else "HIGH" if top[0] >= 61 else "MODERATE" if top[0] >= 31 else "LOW"
    sev_cls = "critical" if severity in {"CRITICAL","HIGH"} else "moderate"
    st.markdown(
        f"""
        <div class='v18-case-card'>
          <div class='v18-case-card-head'>
            <div class='v18-case-icon'>{pcase['icon']}</div>
            <div class='v18-case-id'>{html.escape(pcase['case'])}</div>
          </div>
          <h2>{html.escape(name)}</h2>
          <p class='v18-case-summary'>{html.escape(pcase['summary'])}</p>
          <div class='v18-focus'><span>INVESTIGATION FOCUS</span><b>{html.escape(pcase['focus'])}</b></div>
          <div class='v18-case-finding'>
            <div>
              <span>PRIMARY MODELED CONCERN</span>
              <b>{html.escape(top[2])}</b>
              <small>{html.escape(top[3])} · CMIS {top[0]}</small>
            </div>
            <strong class='{sev_cls}'>{severity}</strong>
          </div>
          <div class='v18-card-metrics'>
            <div><b>{m['components']}</b><span>COMPONENTS</span></div>
            <div><b>{m['assets']}</b><span>CRYPTO ASSETS</span></div>
            <div><b>{m['relationships']}</b><span>ACDKG LINKS</span></div>
          </div>
        </div>
        """, unsafe_allow_html=True)
    return st.button(f"Investigate {pcase['case']}  →", key=f"v18_open_{name}", width="stretch")

def render_runtime_probe():
    st.markdown(
        """
        <div class='v18-secondary-section'>
          <div>
            <div class='v18-eyebrow'>OPTIONAL RUNTIME EVIDENCE</div>
            <h3>Live host probe</h3>
            <p>This is a real, read-only observation of the computer running NEXORA. It demonstrates that the collector is executing; it does not become part of the modeled enterprise case or ACDKG.</p>
          </div>
        </div>
        """, unsafe_allow_html=True)
    if st.button("Run non-invasive host observation", key="v18_probe", width="stretch"):
        st.session_state.local_evidence = local_host_evidence()
        st.rerun()
    if st.session_state.local_evidence:
        ev = st.session_state.local_evidence
        interfaces = ev.get("interfaces") or []
        ports = ev.get("listening_ports") or []
        st.markdown(
            f"""
            <div class='v18-live-result'>
              <div class='v18-live-head'><span>LIVE OBSERVATION · READ ONLY</span><b>{html.escape(ev['timestamp'])}</b></div>
              <div class='v18-live-grid'>
                <div><span>OPERATING SYSTEM</span><b>{html.escape(str(ev['os']))}</b></div>
                <div><span>PYTHON</span><b>{html.escape(str(ev['python']))}</b></div>
                <div><span>PROCESSES</span><b>{html.escape(str(ev['processes'] if ev['processes'] is not None else 'N/A'))}</b></div>
                <div><span>LISTENING PORTS</span><b>{len(ports)}</b></div>
              </div>
              <div class='v18-live-detail'>
                <div><span>HOST</span><b>{html.escape(str(ev['hostname']))}</b></div>
                <div><span>OPENSSL</span><b>{html.escape(str(getattr(__import__('ssl'), 'OPENSSL_VERSION', 'N/A')))}</b></div>
                <div><span>MEMORY</span><b>{html.escape(str(ev.get('memory') or 'N/A'))}</b></div>
                <div><span>INTERFACES</span><b>{html.escape(', '.join(map(str, interfaces)) or 'N/A')}</b></div>
                <div><span>LISTENING TCP PORTS</span><b>{html.escape(', '.join(map(str, ports)) or 'None reported')}</b></div>
              </div>
            </div>
            """, unsafe_allow_html=True)

def stage_field_note(key):
    notes={
        "OVERVIEW":("CRYPTO-AGILITY CONTEXT","Crypto agility is about being able to replace or adapt cryptographic algorithms while preserving security and ongoing operations. This is why NEXORA investigates the surrounding infrastructure, not only the algorithm.","NIST · CSWP 39upd1","https://csrc.nist.gov/pubs/cswp/39/upd1/considerations-for-achieving-crypto-agility/final"),
        "DISCOVERY":("WHY DISCOVERY MATTERS","NIST's PQC migration work identifies cryptographic visibility and risk management as a workstream and describes a cryptographic inventory as a way to understand where and how cryptography is being used.","NIST NCCoE · PQC migration","https://pages.nist.gov/nccoe-migration-post-quantum-cryptography/"),
        "ACDKG":("WHY TRACE MATTERS","Finding a cryptographic asset tells us where it exists. NEXORA now follows the relationships around it to determine what could be affected when that asset changes.","NEXORA investigation method",""),
        "RISK":("WHY ASSESSMENT MATTERS","The inventory does not tell us the operational consequence by itself. NEXORA combines dependency evidence with modeled risk factors and a controlled AI effort signal to explain why migration effort can differ.","NEXORA modeled assessment",""),
        "PLAN":("WHY PLANNING MATTERS","NIST's migration project includes interoperability and benchmarking alongside cryptographic visibility and risk management. NEXORA turns that idea into asset-specific preparation gates in the controlled model.","NIST NCCoE · PQC migration","https://pages.nist.gov/nccoe-migration-post-quantum-cryptography/"),
        "SIMULATE":("WHY SIMULATION MATTERS","NIST's migration work explicitly includes interoperability testing. NEXORA uses a controlled dependency simulation to expose compatibility conditions before treating a modeled change as ready.","NIST NCCoE · migration testing","https://pages.nist.gov/nccoe-migration-post-quantum-cryptography/"),
    }
    return notes.get(key,("FIELD NOTE","NEXORA uses evidence and dependency relationships to reason about migration impact.","NEXORA",""))

def render_footer():
    st.markdown(
        "<div class='v18-footer'><span>NEXORA · controlled academic prototype</span><span>No production infrastructure is modified by this application.</span></div>",
        unsafe_allow_html=True)

# ============================================================
# V18 VISUAL SYSTEM
# ============================================================
st.markdown("""
<style>
:root{
  --v18-bg:#070b10;
  --v18-panel:#0d141c;
  --v18-panel2:#111b25;
  --v18-panel3:#16222e;
  --v18-line:#263646;
  --v18-line2:#34485b;
  --v18-text:#f4f7fb;
  --v18-muted:#8fa0b2;
  --v18-blue:#72b9ff;
  --v18-blue2:#3d83bb;
  --v18-green:#65d19b;
  --v18-red:#ff626a;
  --v18-amber:#e5bd6b;
}
html,body,[data-testid="stAppViewContainer"]{background:var(--v18-bg);color:var(--v18-text)}
[data-testid="stHeader"]{display:flex!important;background:transparent!important;border-bottom:0!important;box-shadow:none!important}
[data-testid="stToolbar"]{display:none!important}
.block-container{max-width:1500px;padding-top:1.15rem!important;padding-bottom:3.5rem!important}
[data-testid="stSidebar"]{background:#0a1017;border-right:1px solid #1d2a37}
[data-testid="stSidebar"]>div{padding-top:1.3rem}
h1,h2,h3{letter-spacing:-.035em}
.stButton>button{border-radius:9px!important;border:1px solid #314457!important;background:#101923!important;color:#edf4fb!important;font-weight:750!important;min-height:2.55rem!important;transition:.16s!important}
.stButton>button:hover{border-color:#5d8db7!important;background:#162534!important;transform:translateY(-1px)!important}\n.stButton>button[kind='primary']{background:#17314a!important;border-color:#5b9bd0!important;color:#f5fbff!important}\n.stButton>button[kind='primary']:hover{background:#1d3e5d!important;border-color:#77b9eb!important}
[data-testid="stSidebar"] .stButton>button{min-height:2.35rem!important}
[data-baseweb="select"]>div{border-radius:9px!important;background:#0d151e!important;border-color:#304253!important}
[data-testid="stDataFrame"]{border:1px solid #293a4b;border-radius:10px;overflow:hidden}
.v18-header{display:flex;justify-content:space-between;align-items:flex-start;gap:25px;padding:5px 2px 14px;border-bottom:1px solid #243340}
.v18-brand{font-size:2.55rem;font-weight:950;letter-spacing:-.075em;line-height:1}
.v18-product{font-size:.68rem;font-weight:850;letter-spacing:.13em;color:#7890a6;margin-top:5px}
.v18-header-case{text-align:right;padding-top:2px}
.v18-case-id{font-size:.64rem;font-weight:850;letter-spacing:.12em;color:#78a8ce}
.v18-case-name{font-size:1.0rem;font-weight:850;margin-top:4px}
.v18-case-focus{font-size:.72rem;color:#8395a8;margin-top:4px}
.v18-context{display:flex;justify-content:space-between;align-items:center;gap:15px;padding:8px 2px 10px;border-bottom:1px solid #1f2d39;color:#899aaa;font-size:.72rem}
.v18-context-label{font-size:.61rem;letter-spacing:.1em;color:#6f8499;margin-right:8px;font-weight:850}
.v18-context b{color:#dce6ef}
.v18-context-right{display:flex;gap:16px;flex-wrap:wrap;justify-content:flex-end}
.v18-context-asset{color:#9bcaf2}
.v18-ribbon-label{font-size:.62rem;letter-spacing:.14em;color:#71869a;font-weight:900;margin:14px 0 5px}
.v18-nav-state{display:none}
.v18-page-intro{display:flex;justify-content:space-between;gap:30px;align-items:flex-end;margin:25px 0 18px;padding-bottom:17px;border-bottom:1px solid #243340}
.v18-page-intro h1{font-size:2.35rem;margin:.25rem 0 .4rem}
.v18-page-intro p{color:#9aabba;margin:0;max-width:930px;line-height:1.55;font-size:.92rem}
.v18-eyebrow{font-size:.62rem;letter-spacing:.14em;font-weight:900;color:#73b8ed;text-transform:uppercase}
.v18-read-panel{background:#0b1219;border:1px solid #273747;border-radius:12px;padding:15px 17px;margin:0 0 18px}
.v18-read-head{font-size:.61rem;font-weight:900;letter-spacing:.13em;color:#6e8498}
.v18-read-question{font-size:1.05rem;font-weight:800;margin:6px 0 12px;color:#e9f1f7}
.v18-read-row{display:inline-flex;gap:8px;margin-right:28px;font-size:.69rem;color:#76899b}
.v18-read-row span{letter-spacing:.08em;font-weight:850}
.v18-read-row b{color:#b6c7d6;font-weight:700}
.v18-section{margin:25px 0 10px}
.v18-section-title{font-size:1.18rem;font-weight:850;margin-bottom:3px}
.v18-section-sub{font-size:.78rem;color:#8394a5;margin-bottom:12px}
.v18-grid-2{display:grid;grid-template-columns:1.35fr .65fr;gap:16px}
.v18-grid-equal{display:grid;grid-template-columns:1fr 1fr;gap:16px}
.v18-panel{background:linear-gradient(180deg,#101923,#0c141c);border:1px solid #293b4c;border-radius:15px;padding:18px}
.v18-panel h3{margin:.2rem 0 .5rem;font-size:1.05rem}
.v18-panel p{color:#98a9b9;line-height:1.6;font-size:.84rem}
.v18-kpi-row{display:grid;grid-template-columns:repeat(4,1fr);border-top:1px solid #273746;border-bottom:1px solid #273746;margin:17px 0 20px}
.v18-kpi{padding:14px 17px;border-right:1px solid #273746}
.v18-kpi:last-child{border-right:none}
.v18-kpi span{display:block;color:#73879a;font-size:.6rem;font-weight:850;letter-spacing:.09em}
.v18-kpi b{display:block;font-size:1.45rem;margin-top:4px;letter-spacing:-.03em}
.v18-kpi small{display:block;color:#8497a8;font-size:.67rem;margin-top:2px}
.v18-asset-hero{background:linear-gradient(135deg,#111d28,#0d151e);border:1px solid #38546b;border-radius:17px;padding:20px;margin:14px 0 20px}
.v18-asset-hero.critical{border-color:#5f3940;background:linear-gradient(135deg,#181419,#10151c)}
.v18-asset-hero.warning{border-color:#665338}
.v18-asset-top{display:flex;justify-content:space-between;gap:18px;align-items:flex-start}
.v18-asset-id{font-family:ui-monospace,monospace;font-size:.74rem;color:#6e94b3;margin-top:4px}
.v18-asset-hero h2{font-size:1.65rem;margin:.2rem 0 .15rem}
.v18-risk-pill{padding:6px 10px;border:1px solid #5b3b42;border-radius:999px;font-size:.64rem;font-weight:900;letter-spacing:.08em;color:#f2a6aa}
.v18-asset-meta{display:grid;grid-template-columns:repeat(4,1fr);gap:0;border-top:1px solid #293a49;border-bottom:1px solid #293a49;margin:16px 0 0}
.v18-asset-meta>div{padding:11px 12px;border-right:1px solid #293a49}
.v18-asset-meta>div:last-child{border-right:none}
.v18-asset-meta span,.v18-asset-stats span{display:block;color:#718699;font-size:.58rem;font-weight:850;letter-spacing:.08em}
.v18-asset-meta b{display:block;margin-top:4px;font-size:.78rem}
.v18-asset-stats{display:grid;grid-template-columns:repeat(4,1fr);margin-top:10px}
.v18-asset-stats>div{padding:5px 12px}
.v18-asset-stats b{display:block;font-size:1rem}
.v18-asset-stats span{font-size:.55rem}
.v18-source-band{display:grid;grid-template-columns:1.2fr .8fr;background:#0e171f;border:1px solid #2c3d4d;border-radius:15px;overflow:hidden;margin-top:27px}
.v18-source-main{padding:21px}
.v18-source-main h2{font-size:1.15rem;margin:.35rem 0 .4rem}
.v18-source-main p{font-size:.79rem;line-height:1.6;color:#9aaaba;margin:0;max-width:700px}
.v18-quote{border-left:1px solid #2c3d4d;padding:21px 24px;background:#0a1118}
.v18-quote-mark{font-size:2.2rem;color:#72b9ff;line-height:.6}
.v18-quote-text{font-size:1.08rem;font-weight:800;line-height:1.35;margin-top:6px}
.v18-quote-source{font-size:.62rem;letter-spacing:.08em;color:#7890a4;margin-top:10px}
.v18-source-links{display:flex;gap:18px;flex-wrap:wrap;padding:10px 2px;color:#75b7ea;font-size:.66rem}
.v18-source-links a{color:#75b7ea;text-decoration:none}
.v18-source-links a:hover{text-decoration:underline}
.v18-case-card{background:linear-gradient(180deg,#101a23,#0c141c);border:1px solid #2c3d4d;border-radius:16px;padding:19px;min-height:395px;transition:.18s}
.v18-case-card:hover{border-color:#4d6d8a;box-shadow:0 16px 40px rgba(0,0,0,.18);transform:translateY(-2px)}
.v18-case-card-head{display:flex;justify-content:space-between;align-items:center}
.v18-case-icon{font-size:1.75rem}.v18-case-card h2{font-size:1.2rem;margin:8px 0}
.v18-case-summary{color:#9cacbc;line-height:1.5;font-size:.78rem;min-height:61px}
.v18-focus{border-top:1px solid #273746;border-bottom:1px solid #273746;padding:11px 0;margin:12px 0}
.v18-focus span,.v18-case-finding span{display:block;color:#70879a;font-size:.57rem;font-weight:900;letter-spacing:.1em}
.v18-focus b{display:block;font-size:.77rem;margin-top:4px}
.v18-case-finding{display:flex;justify-content:space-between;gap:10px;align-items:flex-start;background:#0a1118;border:1px solid #263644;border-radius:10px;padding:11px}
.v18-case-finding b{display:block;font-size:.78rem;margin-top:4px}
.v18-case-finding small{display:block;color:#8396a7;margin-top:3px;font-size:.63rem}
.v18-case-finding strong{font-size:.6rem;letter-spacing:.08em;padding:5px 7px;border:1px solid #4c3940;border-radius:999px;color:#e8a5aa}
.v18-case-finding strong.moderate{color:#e2c684;border-color:#5b5136}
.v18-card-metrics{display:grid;grid-template-columns:repeat(3,1fr);margin-top:12px;border-top:1px solid #273746;border-bottom:1px solid #273746}
.v18-card-metrics>div{padding:9px 7px;border-right:1px solid #273746}
.v18-card-metrics>div:last-child{border-right:none}
.v18-card-metrics b{display:block;font-size:1rem}.v18-card-metrics span{font-size:.53rem;color:#718599;letter-spacing:.06em}
.v18-secondary-section{display:flex;justify-content:space-between;gap:20px;background:#0a1118;border:1px dashed #314354;border-radius:12px;padding:15px 17px;margin:22px 0 10px}
.v18-secondary-section h3{margin:.25rem 0;font-size:.98rem}.v18-secondary-section p{color:#8294a6;font-size:.73rem;line-height:1.55;margin:0;max-width:900px}
.v18-live-result{border:1px solid #2c5948;background:#0b1512;border-radius:14px;margin:13px 0 18px;overflow:hidden}
.v18-live-head{display:flex;justify-content:space-between;gap:10px;padding:11px 14px;border-bottom:1px solid #28483c;color:#91d4b0;font-size:.64rem;letter-spacing:.08em;font-weight:850}
.v18-live-grid{display:grid;grid-template-columns:repeat(4,1fr);border-bottom:1px solid #28483c}
.v18-live-grid>div{padding:13px;border-right:1px solid #28483c}.v18-live-grid>div:last-child{border-right:none}
.v18-live-grid span,.v18-live-detail span{display:block;font-size:.56rem;color:#709985;letter-spacing:.08em;font-weight:850}
.v18-live-grid b{display:block;margin-top:4px;font-size:.85rem;color:#cdebdc}
.v18-live-detail{display:grid;grid-template-columns:1fr 1fr;gap:0}
.v18-live-detail>div{padding:12px 14px;border-bottom:1px solid #28483c}
.v18-live-detail b{display:block;margin-top:4px;font-size:.72rem;color:#b8d9c8;line-height:1.45;word-break:break-word}
.v18-table-head{display:flex;justify-content:space-between;align-items:end;gap:20px;margin:23px 0 9px}
.v18-table-head h2{font-size:1.1rem;margin:0}.v18-table-head p{font-size:.7rem;color:#8194a6;margin:0}
.v18-tabs{display:flex;gap:6px;flex-wrap:wrap;margin-bottom:9px}
.v18-tab-note{font-size:.65rem;color:#74889b;margin:7px 0}
.v18-two-panel{display:grid;grid-template-columns:1.35fr .65fr;gap:15px}
.v18-graph-panel{background:#0a1118;border:1px solid #2b3d4e;border-radius:15px;padding:10px}
.v18-side-panel{background:#0e171f;border:1px solid #293b4b;border-radius:15px;padding:17px}
.v18-side-panel h3{font-size:1rem;margin:.2rem 0 .65rem}.v18-side-panel p{font-size:.76rem;color:#93a5b5;line-height:1.6}
.v18-evidence-row{display:grid;grid-template-columns:repeat(3,1fr);gap:12px;margin:14px 0}
.v18-evidence-box{background:#0c141c;border:1px solid #2a3b4b;border-radius:11px;padding:14px}
.v18-evidence-box strong{font-size:.62rem;letter-spacing:.1em;color:#72b6e9}.v18-evidence-box p{font-size:.72rem;color:#9aabb9;line-height:1.7;margin:.55rem 0 0}
.v18-roadmap{display:grid;grid-template-columns:repeat(5,1fr);gap:8px;margin:15px 0 18px}
.v18-road-step{position:relative;background:#0e171f;border:1px solid #2a3b4b;border-radius:12px;padding:13px;min-height:125px}
.v18-road-step.active{border-color:#4a79a0;background:#11202c}
.v18-road-step .n{font-size:.6rem;color:#72b6e9;font-weight:900;letter-spacing:.1em}
.v18-road-step h3{font-size:.76rem;margin:.45rem 0}.v18-road-step p{font-size:.64rem;color:#8295a7;line-height:1.5}
.v18-sim-switch{display:grid;grid-template-columns:1fr 90px 1fr;align-items:center;gap:12px;margin:17px 0}
.v18-sim-box{background:#0e171f;border:1px solid #2a3b4b;border-radius:13px;padding:18px}
.v18-sim-box.target{border-color:#315f4b;background:#0d1814}
.v18-sim-box h2{font-size:1.45rem;margin:.25rem 0}.v18-sim-box p{color:#8fa1b2;font-size:.72rem;margin:0}
.v18-sim-arrow{text-align:center;font-size:1.8rem;color:#6faedb}
.v18-conclusion{background:linear-gradient(135deg,#121d29,#0d151d);border:1px solid #3b5e7c;border-radius:15px;padding:20px;margin:18px 0}
.v18-conclusion h2{font-size:1.25rem;margin:.35rem 0 .5rem}.v18-conclusion p{color:#9eafbf;line-height:1.6;margin:0}
.v18-footer{display:flex;justify-content:space-between;gap:15px;border-top:1px solid #1f2d39;margin-top:35px;padding-top:12px;color:#667a8e;font-size:.62rem}
.v18-side-head{font-size:.63rem;color:#71879a;font-weight:900;letter-spacing:.12em;margin-bottom:7px}
.v18-side-case{font-size:1.0rem;font-weight:850;line-height:1.25}.v18-side-id{font-size:.65rem;color:#7890a4;margin-top:4px}
.v18-side-block{padding:14px 0;border-top:1px solid #22313f}
.v18-side-metric{display:flex;justify-content:space-between;align-items:center;padding:6px 0;color:#8396a7;font-size:.68rem}
.v18-side-metric b{color:#dbe5ee;font-size:.78rem}
.v18-side-stage{background:#101b25;border:1px solid #2c4357;border-radius:10px;padding:11px;margin-top:9px}
.v18-side-stage b{display:block;color:#e6eef5;font-size:.76rem}.v18-side-stage span{display:block;color:#7f93a6;font-size:.64rem;line-height:1.45;margin-top:4px}
@media(max-width:1000px){
 .v18-header{flex-direction:column}.v18-header-case{text-align:left}
 .v18-context{flex-direction:column;align-items:flex-start}.v18-context-right{justify-content:flex-start}
 .v18-grid-2,.v18-two-panel,.v18-grid-equal{grid-template-columns:1fr}
 .v18-kpi-row{grid-template-columns:1fr 1fr}.v18-asset-meta,.v18-asset-stats,.v18-live-grid,.v18-roadmap{grid-template-columns:1fr 1fr}
 .v18-evidence-row{grid-template-columns:1fr}.v18-source-band{grid-template-columns:1fr}.v18-quote{border-left:none;border-top:1px solid #2c3d4d}
}

.v18-hero{background:linear-gradient(135deg,#12202c 0%,#0d151e 65%,#101922 100%);border:1px solid #31485c;border-radius:20px;padding:34px 38px;margin:20px 0 27px;box-shadow:0 18px 55px rgba(0,0,0,.2);position:relative;overflow:hidden}
.v18-hero:after{content:"";position:absolute;right:-100px;top:-120px;width:380px;height:380px;border:1px solid rgba(114,185,255,.09);border-radius:50%;box-shadow:0 0 0 40px rgba(114,185,255,.025),0 0 0 80px rgba(114,185,255,.018);pointer-events:none}
.v18-hero h1{font-size:2.55rem;line-height:1.08;max-width:900px;margin:.4rem 0 .75rem}
.v18-hero p{max-width:900px;color:#a7b7c6;font-size:.96rem;line-height:1.65;margin:0}
.v18-hero-flow{display:flex;gap:10px;align-items:center;flex-wrap:wrap;margin-top:21px}
.v18-hero-flow span{padding:7px 10px;border:1px solid #344d62;background:#0b141d;border-radius:8px;font-size:.62rem;font-weight:900;letter-spacing:.09em;color:#9ec8e8}
.v18-hero-flow i{font-style:normal;color:#55728b}
.v18-bottom-grid{display:grid;grid-template-columns:1fr 1fr;gap:15px;margin-top:22px}
@media(max-width:900px){.v18-bottom-grid{grid-template-columns:1fr}}
</style>
""", unsafe_allow_html=True)

# ============================================================
# V20 REFINEMENT LAYER
# ============================================================
st.markdown("""
<style>
/* V20 hierarchy: larger meaning, quieter supporting evidence */
.v20-side-brand{font-size:.62rem;font-weight:900;letter-spacing:.18em;color:#78b7e8;margin:3px 0 7px}
.v20-side-product{font-size:1.05rem;font-weight:900;line-height:1.16;color:#f2f6fa}
.v20-side-id{font-size:.64rem;color:#7295b2;margin-top:7px}
.v20-side-block{border-top:1px solid #22313f;padding:15px 0 3px;margin-top:14px}
.v20-side-head{font-size:.58rem;font-weight:900;letter-spacing:.13em;color:#71879a;margin-bottom:9px}
.v20-work-step{display:flex;gap:9px;align-items:flex-start;padding:7px 7px;border-left:2px solid #1e2d3b;margin:2px 0;color:#72869a}
.v20-work-step span{font:700 .58rem ui-monospace,monospace;color:#52697c;padding-top:1px}
.v20-work-step b{display:block;font-size:.67rem;color:#8da0b1;letter-spacing:.02em}
.v20-work-step small{display:block;font-size:.58rem;color:#617486;line-height:1.35;margin-top:2px}
.v20-work-step.active{border-left-color:#6db7ef;background:#0e1a25;border-radius:0 7px 7px 0}
.v20-work-step.active span,.v20-work-step.active b{color:#e9f4fc}
.v20-work-step.done b{color:#a6b8c7}
.v20-field-note{border:1px solid #2a3d4e;background:#0c151e;border-radius:11px;padding:13px 12px;margin:17px 0 10px}
.v20-note-label{font-size:.57rem;font-weight:900;letter-spacing:.12em;color:#70b5e8}
.v20-field-note p{font-size:.67rem;line-height:1.55;color:#91a3b3;margin:7px 0 8px}
.v20-note-source{font-size:.56rem;color:#5f819d;font-weight:800}
.v20-current-stage{border-top:1px solid #22313f;padding:12px 0 3px;margin-top:10px}
.v20-current-stage span{display:block;font-size:.57rem;letter-spacing:.12em;font-weight:900;color:#6c8397}
.v20-current-stage b{display:block;font-size:.75rem;color:#e4edf4;margin-top:4px}
.v20-current-stage small{display:block;color:#778c9e;font-size:.61rem;line-height:1.4;margin-top:4px}
.v20-home-hero{position:relative;overflow:hidden;border:1px solid #30495f;border-radius:25px;padding:43px 45px;margin:13px 0 29px;background:linear-gradient(135deg,#12202d,#0a1118 62%,#101c28);box-shadow:0 22px 70px rgba(0,0,0,.25)}
.v20-home-hero:after{content:"";position:absolute;right:-120px;top:-190px;width:470px;height:470px;border:1px solid rgba(114,185,255,.11);border-radius:50%;box-shadow:0 0 0 55px rgba(114,185,255,.022),0 0 0 110px rgba(114,185,255,.014);pointer-events:none}
.v20-home-hero h1{position:relative;font-size:2.95rem;line-height:1.04;letter-spacing:-.055em;max-width:1000px;margin:8px 0 14px}.v20-home-hero>p{position:relative;color:#a7b8c7;font-size:1rem;line-height:1.7;max-width:970px;margin:0}
.v20-home-answer{position:relative;max-width:900px;border-top:1px solid #294050;margin-top:25px;padding-top:16px}.v20-home-answer span{display:block;color:#6fb7f3;font-size:.61rem;font-weight:900;letter-spacing:.14em}.v20-home-answer b{display:block;font-size:1.08rem;line-height:1.45;margin-top:5px}
.v20-home-flow{position:relative;display:flex;align-items:center;gap:9px;margin-top:25px;flex-wrap:wrap}.v20-home-flow>div{display:grid;grid-template-columns:auto auto;column-gap:7px;align-items:center;border:1px solid #2d465b;background:#0b151f;border-radius:9px;padding:8px 10px}.v20-home-flow strong{grid-row:span 2;font:800 .62rem ui-monospace,monospace;color:#5e90b8}.v20-home-flow b{font-size:.66rem;letter-spacing:.08em}.v20-home-flow span{font-size:.59rem;color:#7e93a6}.v20-home-flow i{font-style:normal;color:#547189}
.v20-section-head{display:flex;justify-content:space-between;align-items:end;gap:25px;margin:0 0 12px}.v20-section-head>div>span{font-size:.61rem;letter-spacing:.13em;font-weight:900;color:#6eadd8}.v20-section-head h2{font-size:1.42rem;margin:5px 0 0}.v20-section-head>p{max-width:460px;color:#8295a7;font-size:.72rem;line-height:1.5;margin:0}.v20-work-head{margin-top:31px}
.v20-case-card{background:linear-gradient(180deg,#111b25,#0b131b);border:1px solid #2b3e50;border-radius:17px;padding:19px;min-height:410px;display:flex;flex-direction:column;transition:.18s}.v20-case-card:hover{border-color:#4d7396;transform:translateY(-3px);box-shadow:0 17px 42px rgba(0,0,0,.18)}
.v20-case-top{display:flex;justify-content:space-between;align-items:center;color:#6689a5;font-size:.62rem;font-weight:900;letter-spacing:.1em}.v20-case-icon{font-size:1.55rem}.v20-case-card h3{font-size:1.25rem;margin:13px 0 8px}.v20-case-card>p{font-size:.79rem;color:#9babb9;line-height:1.55;min-height:54px;margin:0}.v20-case-question{border-top:1px solid #263746;border-bottom:1px solid #263746;padding:12px 0;margin:14px 0}.v20-case-question span,.v20-case-start span{display:block;font-size:.56rem;font-weight:900;letter-spacing:.1em;color:#68839a}.v20-case-question b{display:block;font-size:.76rem;margin-top:5px;line-height:1.4}.v20-case-path{display:flex;align-items:center;gap:5px;flex-wrap:wrap;margin:1px 0 13px}.v20-case-path span{padding:5px 7px;border:1px solid #2c4255;border-radius:6px;font-size:.59rem;color:#9eb9ce}.v20-case-path i{font-style:normal;color:#58748a;font-size:.65rem}.v20-case-metrics{display:grid;grid-template-columns:repeat(3,1fr);border-top:1px solid #263746;border-bottom:1px solid #263746;margin-top:auto}.v20-case-metrics div{padding:9px 6px;border-right:1px solid #263746}.v20-case-metrics div:last-child{border-right:0}.v20-case-metrics b{display:block;font-size:1rem}.v20-case-metrics span{font-size:.52rem;color:#70869a;letter-spacing:.05em}.v20-case-start{padding:11px 0 0}.v20-case-start b{display:block;font-size:.75rem;margin-top:4px}.v20-case-start small{display:block;font-size:.6rem;color:#71869a;margin-top:3px}.v20-case-card + .stButton{margin-top:9px}
.v20-brief-divider{border-top:1px solid #233440;margin:29px 0 20px}.v20-case-brief{display:grid;grid-template-columns:1.2fr .8fr;border:1px solid #36526a;border-radius:18px;background:linear-gradient(135deg,#111d28,#0b141c);overflow:hidden;box-shadow:0 18px 45px rgba(0,0,0,.16)}.v20-brief-main{padding:24px 26px}.v20-brief-main h2{font-size:2rem;margin:5px 0 8px}.v20-brief-summary{color:#9eafbe;font-size:.88rem;line-height:1.65;max-width:760px}.v20-brief-question{border-left:3px solid #65afe6;padding-left:14px;margin:18px 0}.v20-brief-question span{display:block;font-size:.58rem;color:#70b6e9;font-weight:900;letter-spacing:.11em}.v20-brief-question b{display:block;font-size:.96rem;line-height:1.5;margin-top:5px}.v20-brief-why{color:#8da0b1;font-size:.76rem;line-height:1.6}.v20-brief-evidence{display:grid;grid-template-columns:1fr 1fr;background:#091119;border-left:1px solid #2b4051}.v20-brief-evidence>div{padding:17px;border-bottom:1px solid #263746}.v20-brief-evidence>div:nth-child(odd){border-right:1px solid #263746}.v20-brief-evidence span{display:block;font-size:.55rem;color:#6c879d;font-weight:900;letter-spacing:.09em}.v20-brief-evidence b{display:block;font-size:1rem;margin-top:5px}.v20-brief-evidence small{display:block;color:#7f93a5;font-size:.6rem;line-height:1.45;margin-top:4px}
.v20-home-steps{display:grid;grid-template-columns:repeat(5,1fr);border-top:1px solid #273a49;border-bottom:1px solid #273a49;background:#0a1118}.v20-home-steps>div{padding:16px 14px;border-right:1px solid #243543}.v20-home-steps>div:last-child{border-right:0}.v20-home-steps strong{display:block;font:800 .62rem ui-monospace,monospace;color:#5f91b8}.v20-home-steps b{display:block;font-size:.82rem;margin-top:6px}.v20-home-steps span{display:block;font-size:.7rem;color:#d7e3ec;margin-top:5px}.v20-home-steps small{display:block;font-size:.61rem;color:#708597;line-height:1.45;margin-top:4px}
.v20-research{margin-top:28px;border-top:1px solid #273a49;padding-top:19px}.v20-research-head{display:flex;justify-content:space-between;align-items:end;gap:25px}.v20-research-head>div>span{font-size:.59rem;letter-spacing:.13em;color:#6ca8d2;font-weight:900}.v20-research-head h2{font-size:1.18rem;margin:5px 0 0}.v20-research-head>p{font-size:.68rem;color:#718699;max-width:430px;margin:0;line-height:1.5}.v20-research-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:24px;margin-top:14px}.v20-research-grid>div{padding:13px 0;border-top:1px solid #253643}.v20-research-grid b{font-size:.59rem;letter-spacing:.1em;color:#7594ab}.v20-research-grid p{font-size:.71rem;color:#899baa;line-height:1.5;margin:6px 0 8px}.v20-research-grid a{font-size:.65rem;color:#70b6eb;text-decoration:none}.v20-research-grid a:hover{text-decoration:underline}.v20-boundary{display:flex;justify-content:space-between;gap:30px;border-top:1px solid #273a49;margin-top:25px;padding:18px 0}.v20-boundary span{font-size:.58rem;letter-spacing:.12em;color:#6d879c;font-weight:900}.v20-boundary h3{font-size:1rem;margin:5px 0 0}.v20-boundary p{max-width:780px;color:#8497a8;font-size:.7rem;line-height:1.55;margin:0}

/* ============================================================
   V22 — EXPLANATION + DECISION CLARITY + READABILITY
   Refinement layer on top of V20. Graph layout intentionally preserved; readability and helper ordering corrected.
   ============================================================ */
.v21-vertical-note{display:flex;gap:13px;margin:14px 0;padding:4px 0 4px 0}.v21-vertical-bar{width:3px;min-width:3px;background:#5aaeea;border-radius:3px}.v21-vertical-note span{display:block;font-size:.57rem;font-weight:900;letter-spacing:.12em;color:#6fb7ee}.v21-vertical-note h4{font-size:.86rem;margin:5px 0 5px;color:#e4edf4}.v21-vertical-note p{font-size:.72rem;line-height:1.62;color:#8ea2b3;margin:0;max-width:720px}
.v21-insight-panel{border-left:3px solid #477b9f;padding:8px 0 8px 16px;margin:2px 0 20px}.v21-insight-panel.selected{border-left-color:#69b8ef}.v21-insight-panel>span{display:block;font-size:.58rem;letter-spacing:.12em;font-weight:900;color:#6fb5e8}.v21-insight-panel h3{font-size:1.15rem;margin:6px 0 7px}.v21-insight-panel>p{font-size:.76rem;color:#899eaf;line-height:1.6;margin:0 0 10px}.v21-insight-line{display:flex;justify-content:space-between;gap:12px;border-bottom:1px solid #22313e;padding:7px 0;font-size:.69rem}.v21-insight-line b{color:#738da3;font-weight:800}.v21-insight-line span{color:#d7e3eb;text-align:right}.v21-insight-emphasis{color:#b7c9d7!important;margin-top:13px!important}.v21-big-pair{display:flex;align-items:baseline;gap:8px;margin:5px 0 8px}.v21-big-pair b{font-size:1.22rem}.v21-big-pair span{font-size:.67rem;color:#8297a9}
.v21-transition-note{border-top:1px solid #263845;border-bottom:1px solid #263845;padding:12px 2px;margin:18px 0 20px;color:#8da1b2;font-size:.74rem;line-height:1.55}.v21-transition-note b{color:#dce8ef}
.v21-assess-primary{background:linear-gradient(180deg,#0f1923,#0b131b);border:1px solid #2c4052;border-radius:14px;padding:20px}.v21-assess-primary>span,.v21-ai-panel>span{font-size:.58rem;font-weight:900;letter-spacing:.12em;color:#70b6e9}.v21-cmis-line{display:flex;align-items:baseline;gap:9px;margin-top:5px}.v21-cmis-line b{font-size:3rem;letter-spacing:-.06em}.v21-cmis-line span{font-size:.74rem;color:#7f94a6}.v21-assess-primary>p,.v21-ai-panel>p{font-size:.73rem;color:#8296a8;line-height:1.55;margin:0 0 12px}.v21-factor{display:flex;justify-content:space-between;padding:10px 0;border-top:1px solid #263744;font-size:.72rem}.v21-factor span{color:#8ba0b0}.v21-factor b{color:#e0ebf2}.v21-ai-panel{background:#0f1923;border:1px solid #30495e;border-radius:14px;padding:20px}.v21-ai-title{font-size:2.1rem;font-weight:900;letter-spacing:-.04em;margin:7px 0 3px}.v21-metric-pair{display:grid;grid-template-columns:1fr 1fr;border-top:1px solid #293b49;margin-top:15px}.v21-metric-pair>div{padding:12px 10px 4px 0}.v21-metric-pair>div+div{border-left:1px solid #293b49;padding-left:14px}.v21-metric-pair b{display:block;font-size:1.15rem}.v21-metric-pair span{display:block;font-size:.53rem;letter-spacing:.08em;color:#71879a;margin-top:3px}.v21-stage-conclusion{border-left:3px solid #6cb8ee;padding:9px 0 9px 16px;margin:20px 0}.v21-stage-conclusion>span{display:block;font-size:.58rem;letter-spacing:.12em;color:#6eb5e8;font-weight:900}.v21-stage-conclusion>b{display:block;font-size:.92rem;margin-top:6px}.v21-stage-conclusion p{font-size:.75rem;line-height:1.6;color:#8ea1b2;margin:7px 0 0}
.v21-validation-list{border-top:1px solid #263744}.v21-validation-list .v19-check{padding:12px 0}.v21-final-conclusion{background:linear-gradient(135deg,#132230,#0b141c);border:1px solid #4a7394;border-radius:17px;padding:26px 27px;margin:26px 0 17px;box-shadow:0 20px 50px rgba(0,0,0,.18)}.v21-final-kicker{font-size:.6rem;letter-spacing:.14em;color:#70b9ef;font-weight:900}.v21-final-conclusion h2{font-size:1.5rem;line-height:1.35;margin:7px 0 17px;max-width:1050px}.v21-final-most{border-left:3px solid #6db8ee;padding:7px 0 7px 15px;margin:12px 0 18px}.v21-final-most span,.v21-final-grid span,.v21-final-answer span{display:block;font-size:.57rem;font-weight:900;letter-spacing:.11em;color:#6eadd7}.v21-final-most b{display:block;font-size:.94rem;line-height:1.55;margin-top:5px;color:#e2edf3}.v21-final-grid{display:grid;grid-template-columns:1fr 1fr;gap:26px;border-top:1px solid #294050;border-bottom:1px solid #294050;padding:15px 0}.v21-final-grid p{font-size:.75rem;line-height:1.65;color:#94a8b8;margin:6px 0 0}.v21-final-answer{margin-top:17px}.v21-final-answer b{display:block;font-size:1rem;line-height:1.5;margin-top:5px;color:#e5eef4}.v21-final-conclusion>small{display:block;color:#6f8395;font-size:.61rem;line-height:1.5;margin-top:16px}.v21-case-finding{border-top:1px solid #263744;border-bottom:1px solid #263744;padding:14px 0;margin:12px 0 0}.v21-case-finding span{display:block;font-size:.58rem;letter-spacing:.12em;color:#6b8da5;font-weight:900}.v21-case-finding b{display:block;font-size:.9rem;margin-top:5px}.v21-case-finding p{font-size:.7rem;color:#8296a8;margin:4px 0 0}
.v21-side-trail{border-top:1px solid #22313f;margin-top:14px;padding-top:12px}.v21-trail-row{display:grid;grid-template-columns:22px 62px 1fr;gap:6px;align-items:baseline;padding:6px 0;border-left:2px solid #1d2b38;padding-left:7px}.v21-trail-row span{font:700 .54rem ui-monospace,monospace;color:#536a7d}.v21-trail-row b{font-size:.59rem;color:#708699;letter-spacing:.04em}.v21-trail-row em{font-style:normal;font-size:.53rem;color:#536a7c;line-height:1.3}.v21-trail-row.complete{border-left-color:#34566f}.v21-trail-row.complete b{color:#a3b7c7}.v21-trail-row.current{border-left-color:#6bb7ed;background:#0c1822;border-radius:0 6px 6px 0}.v21-trail-row.current b,.v21-trail-row.current em{color:#e1edf5}
.v20-current-stage em{display:block;font-style:normal;color:#6f9abb;font-size:.55rem;line-height:1.4;margin-top:5px}
.v20-note-source a{color:#69afe1;text-decoration:none}.v20-note-source a:hover{text-decoration:underline}
.v21-home-propagation{display:grid;grid-template-columns:.9fr 1.6fr;gap:25px;border:1px solid #2b4356;border-radius:16px;background:#0b141d;padding:18px 20px;margin:0 0 28px}.v21-prop-intro span{display:block;font-size:.58rem;letter-spacing:.12em;font-weight:900;color:#6eadd7}.v21-prop-intro h3{font-size:1.12rem;line-height:1.35;margin:6px 0}.v21-prop-intro p{font-size:.7rem;line-height:1.55;color:#8397a8;margin:0}.v21-prop-chain{display:flex;align-items:center;gap:8px;justify-content:flex-end}.v21-prop-chain>div{border-top:2px solid #36546b;padding:9px 8px 0;min-width:125px}.v21-prop-chain b{display:block;font-size:.58rem;letter-spacing:.08em}.v21-prop-chain span{display:block;font-size:.59rem;color:#71879a;margin-top:4px;line-height:1.35}.v21-prop-chain i{font-style:normal;color:#5b87a8;font-size:1.05rem}
@media(max-width:1000px){.v21-final-grid{grid-template-columns:1fr}.v21-home-propagation{grid-template-columns:1fr}.v21-prop-chain{justify-content:flex-start;flex-wrap:wrap}.v21-trail-row{grid-template-columns:22px 70px 1fr}}

/* Improve stage typography without changing layout */
.v19-page-intro h1{font-size:2.55rem!important}.v19-finding h2{font-size:1.42rem!important;line-height:1.35}.v19-readout h3{font-size:1.22rem!important}.v19-readout .lead{font-size:1rem!important;line-height:1.6}.v19-table-caption h3{font-size:1.14rem!important}.v19-table-caption p{font-size:.76rem!important}.v19-runtime-head h3{font-size:1.25rem!important}.v19-runtime-head p{font-size:.8rem!important}.v19-runtime-cell b{font-size:.9rem!important}.v19-runtime-detail{font-size:.76rem!important}.v19-road-step{padding:18px 15px 19px;background:linear-gradient(180deg,#0e1923,#0b131b)}.v19-road-step .n{font-size:.68rem}.v19-road-step b{font-size:.86rem;margin-top:7px}.v19-road-step p{font-size:.73rem;line-height:1.55}.v19-gate{grid-template-columns:145px 1fr;padding:13px 0}.v19-gate span{font-size:.64rem}.v19-gate b{font-size:.82rem;line-height:1.45}.v19-conclusion h2{font-size:1.3rem}.v19-conclusion p{font-size:.82rem}.v19-check,.v19-conflict{font-size:.8rem;padding:10px 0}.v19-graph-reading{font-size:.8rem}.v19-path-node{font-size:.69rem}
@media(max-width:1000px){.v20-case-brief{grid-template-columns:1fr}.v20-brief-evidence{border-left:0;border-top:1px solid #2b4051}.v20-home-steps{grid-template-columns:1fr 1fr}.v20-home-steps>div:nth-child(2n){border-right:0}.v20-research-grid{grid-template-columns:1fr}.v20-section-head,.v20-research-head,.v20-boundary{align-items:flex-start;flex-direction:column}.v20-home-hero h1{font-size:2.35rem}}

/* ============================================================
   V27 — readable evidence, real local collection, assessment
   ============================================================ */
.v27-runtime-banner{display:flex;justify-content:space-between;gap:28px;align-items:center;margin:22px 0 18px;padding:24px 28px;border:1px solid #355873;border-radius:17px;background:linear-gradient(135deg,#102232,#0b151e)}
.v27-runtime-banner>div:first-child>span,.v27-section>span,.v27-assess-purpose>span,.v27-chart-card>span,.v27-ai-result span,.v27-assess-chain span,.v27-interpret-card>span{display:block;color:#70b9ee;font-size:.78rem;font-weight:900;letter-spacing:.13em}
.v27-runtime-banner h2{font-size:1.55rem;line-height:1.3;margin:7px 0 6px}.v27-runtime-banner p{font-size:1rem;line-height:1.7;color:#aebfcd;margin:0;max-width:950px}
.v27-collector-badge{border:1px solid #416781;border-radius:12px;padding:12px 16px;color:#79bce9;font-size:.72rem;font-weight:900;letter-spacing:.1em;text-align:center;min-width:150px}.v27-collector-badge b{font-size:.9rem;color:#e3eef5;letter-spacing:0}
.v27-kpi-grid{display:grid;grid-template-columns:repeat(6,1fr);border:1px solid #30485d;border-radius:16px;overflow:hidden;background:#0d151e;margin:18px 0 28px}.v27-kpi-grid>div{padding:19px 18px;min-height:112px;border-right:1px solid #263b4d}.v27-kpi-grid>div:last-child{border-right:0}.v27-kpi-grid span{display:block;font-size:.72rem;color:#70b9ee;font-weight:900;letter-spacing:.11em}.v27-kpi-grid b{display:block;font-size:1.28rem;line-height:1.25;color:#edf5fa;margin-top:8px;overflow-wrap:anywhere}.v27-kpi-grid small{display:block;font-size:.86rem;color:#9fb1c1;line-height:1.45;margin-top:6px}
.v27-section{margin:10px 0 10px}.v27-section h3,.v27-chart-card h3{font-size:1.45rem;line-height:1.3;margin:6px 0}.v27-section p,.v27-chart-card p{font-size:1rem;line-height:1.7;color:#9eb1c0;margin:0}
.v27-assess-purpose{margin:8px 0 26px;padding:27px 30px;border:1px solid #3b5c72;border-radius:18px;background:linear-gradient(145deg,#10212d,#0b151e)}.v27-assess-purpose h2{font-size:1.75rem;line-height:1.3;margin:8px 0 12px}.v27-assess-purpose p{font-size:1.05rem;line-height:1.8;color:#adbfcc;max-width:1050px;margin:0}
.v27-assess-kpi{padding:19px 17px;border:1px solid #2f485c;border-radius:14px;background:#0c1720;min-height:126px}.v27-assess-kpi span{font-size:.72rem;color:#70b9ee;font-weight:900;letter-spacing:.11em}.v27-assess-kpi b{display:block;font-size:1.45rem;line-height:1.25;margin-top:8px;overflow-wrap:anywhere}.v27-assess-kpi small{display:block;color:#91a6b5;font-size:.84rem;line-height:1.45;margin-top:6px}
.v27-chart-card{margin-bottom:5px}.v27-chart-card h3{font-size:1.35rem}.v27-chart-card p{font-size:.96rem}
.v27-score-explanation{margin-top:10px;padding:16px 18px;border-left:3px solid #6eb8ea;background:#0c1822}.v27-score-explanation b{display:inline-block;font-size:1.05rem;margin-right:12px}.v27-score-explanation span{font-size:1rem;color:#8fc4e7}.v27-score-explanation p{font-size:.94rem;line-height:1.7;color:#9fb1c0;margin:7px 0 0}
.v27-ai-result{display:grid;grid-template-columns:1.35fr .65fr;gap:28px;margin:28px 0;padding:27px 30px;border:1px solid #3d6078;border-radius:18px;background:linear-gradient(145deg,#112433,#0a151e)}.v27-ai-result h2{font-size:1.8rem;margin:7px 0 9px}.v27-ai-result p{font-size:1rem;line-height:1.75;color:#aebfcd;margin:0}.v27-ai-metrics{display:grid;grid-template-columns:1fr 1fr;border-left:1px solid #304a5e;padding-left:26px}.v27-ai-metrics>div{padding:8px 14px;border-bottom:1px solid #2b4253}.v27-ai-metrics b{display:block;font-size:1.7rem}.v27-ai-metrics span{display:block;font-size:.7rem;margin-top:4px}.v27-ai-metrics small{display:block;color:#94a8b7;font-size:.84rem;line-height:1.55;margin-top:5px}
.v27-assess-chain{display:grid;grid-template-columns:repeat(4,1fr);border:1px solid #2f485a;border-radius:16px;overflow:hidden;background:#0b151d;margin:25px 0}.v27-assess-chain>div{padding:20px;border-right:1px solid #293f50;min-height:150px}.v27-assess-chain>div:last-child{border-right:0}.v27-assess-chain span{font-size:.72rem}.v27-assess-chain b{display:block;font-size:1.05rem;line-height:1.4;margin:8px 0}.v27-assess-chain small{display:block;font-size:.88rem;line-height:1.55;color:#91a6b5}
.v27-interpret-card{border-top:1px solid #2c4455;padding:22px 4px}.v27-interpret-card h3{font-size:1.35rem;margin:7px 0 9px}.v27-interpret-card p{font-size:1rem;line-height:1.75;color:#9fb2c0;margin:6px 0}
.v27-sim-result{display:grid;grid-template-columns:1fr auto;align-items:center;gap:25px;margin:26px 0 24px;padding:25px 28px;border:1px solid #4d7797;border-left:5px solid #67b9ed;border-radius:16px;background:linear-gradient(145deg,#122534,#0b151e);overflow:visible;box-sizing:border-box;width:100%}.v27-sim-result.blocked{border-left-color:#c57b86}.v27-sim-result span{display:block;color:#70b9ee;font-size:.78rem;font-weight:900;letter-spacing:.13em}.v27-sim-result h2{font-size:1.8rem;line-height:1.25;margin:7px 0}.v27-sim-result p{font-size:1.03rem;line-height:1.75;color:#aabcc9;margin:0}.v27-sim-result-meta{min-width:160px;text-align:center;border-left:1px solid #2e4a5c;padding-left:25px}.v27-sim-result-meta b{display:block;font-size:2.1rem}.v27-sim-result-meta span{font-size:.68rem}
.v26-sim-action-note{overflow:visible;box-sizing:border-box;width:100%;padding:21px 24px!important}.v26-sim-action-note b{font-size:1.2rem!important;line-height:1.45!important}.v26-sim-action-note p{font-size:1rem!important;line-height:1.75!important;overflow-wrap:anywhere}
.v19-check,.v19-conflict{overflow-wrap:anywhere}.v21-vertical-note,.v21-stage-conclusion,.v21-insight-panel{overflow-wrap:anywhere}
@media(max-width:1200px){.v27-kpi-grid{grid-template-columns:repeat(3,1fr)}.v27-kpi-grid>div:nth-child(3){border-right:0}.v27-kpi-grid>div:nth-child(n+4){border-top:1px solid #263b4d}.v27-assess-chain{grid-template-columns:1fr 1fr}.v27-assess-chain>div:nth-child(2){border-right:0}.v27-assess-chain>div:nth-child(n+3){border-top:1px solid #293f50}.v27-ai-result{grid-template-columns:1fr}.v27-ai-metrics{border-left:0;border-top:1px solid #304a5e;padding:15px 0 0}}
@media(max-width:800px){.v27-runtime-banner{flex-direction:column;align-items:flex-start}.v27-kpi-grid{grid-template-columns:1fr 1fr}.v27-kpi-grid>div:nth-child(2n){border-right:0}.v27-kpi-grid>div:nth-child(n+3){border-top:1px solid #263b4d}.v27-assess-chain{grid-template-columns:1fr}.v27-assess-chain>div{border-right:0;border-top:1px solid #293f50}.v27-assess-chain>div:first-child{border-top:0}.v27-sim-result{grid-template-columns:1fr}.v27-sim-result-meta{border-left:0;border-top:1px solid #2e4a5c;padding:14px 0 0;text-align:left}}

/* ============================================================
   V31 — RESTORED V28 FOUNDATION + INVESTIGATION CLARITY
   ============================================================ */
.v31-audience{display:grid;grid-template-columns:1.05fr 1.95fr;gap:24px;margin:28px 0;padding:30px;border:1px solid #385b73;border-radius:20px;background:linear-gradient(145deg,#102330,#0b141c)}
.v31-audience-intro h2{font-size:1.8rem;line-height:1.25;margin:7px 0 12px}.v31-audience-intro p{font-size:.98rem;line-height:1.7;color:#aebfcd}.v31-audience-grid{display:grid;grid-template-columns:1fr 1fr;gap:12px}.v31-audience-card{padding:18px;border:1px solid #294557;border-radius:14px;background:#0a151e;min-height:130px}.v31-audience-card .role{color:#72b9ee;font-size:.67rem;font-weight:900;letter-spacing:.1em}.v31-audience-card h3{font-size:1.02rem;margin:6px 0}.v31-audience-card p{font-size:.82rem;line-height:1.55;color:#91a6b5;margin:0}.v31-knowledge-map{display:grid;grid-template-columns:repeat(3,1fr);gap:14px;margin-top:17px}.v31-knowledge-card{padding:20px;border:1px solid #304b5d;border-radius:15px;background:#0a131b;min-height:145px}.v31-knowledge-card .level{color:#70b9ee;font-size:.67rem;font-weight:900;letter-spacing:.11em}.v31-knowledge-card h3{font-size:1.08rem;margin:7px 0}.v31-knowledge-card p{font-size:.84rem;line-height:1.6;color:#94a8b7;margin:0}.v31-not-needed{margin-top:16px;padding:12px 15px;border-left:3px solid #65d19b;background:#0b1713;color:#a8dfc1;font-size:.84rem;line-height:1.55}.v31-io{display:grid;grid-template-columns:1fr 170px 1fr;align-items:stretch;border:1px solid #304b5d;border-radius:19px;overflow:hidden;background:#0b151d;margin:26px 0}.v31-io-side{padding:27px}.v31-io-side.input{border-right:1px solid #2e4a5e}.v31-io-side.output{border-left:1px solid #2e4a5e}.v31-io-side .tag{display:inline-block;padding:5px 9px;border:1px solid #35566d;border-radius:999px;color:#70b9ee;font-size:.67rem;font-weight:900;letter-spacing:.08em}.v31-io-side h3{font-size:1.28rem;margin:8px 0 14px}.v31-io-side ul{margin:0;padding-left:20px}.v31-io-side li{font-size:.86rem;line-height:1.7;color:#b0c0cd;margin:4px 0}.v31-io-engine{display:flex;align-items:center;justify-content:center;padding:20px;background:linear-gradient(180deg,#112536,#0d1922);position:relative}.v31-io-engine:before,.v31-io-engine:after{content:'';position:absolute;left:0;right:0;height:1px;background:#36566b}.v31-io-engine:before{top:28%}.v31-io-engine:after{bottom:28%}.v31-engine-box{position:relative;z-index:2;padding:17px 13px;border:1px solid #5d8eb2;border-radius:14px;background:#10202d;text-align:center;box-shadow:0 12px 35px rgba(0,0,0,.25)}.v31-engine-box span{display:block;color:#70b9ee;font-size:.62rem;font-weight:900;letter-spacing:.11em}.v31-engine-box b{display:block;font-size:1.05rem;margin-top:5px}.v31-engine-box small{display:block;color:#90a7b8;font-size:.68rem;line-height:1.45;margin-top:5px}.v31-bridge{margin:32px 0;border:1px solid #334c5d;border-radius:20px;overflow:hidden;background:#0a1118}.v31-bridge-head{padding:28px 30px;border-bottom:1px solid #2d4352;background:linear-gradient(135deg,#101d27,#0c151d)}.v31-bridge-head .eyebrow{color:#72b9ee;font-size:.7rem;font-weight:900;letter-spacing:.13em}.v31-bridge-head h2{font-size:2rem;line-height:1.25;margin:8px 0}.v31-bridge-head p{font-size:.93rem;line-height:1.6;color:#9db0bf;margin:0;max-width:1100px}.v31-bridge-labels{display:grid;grid-template-columns:1fr 70px 1fr;border-bottom:1px solid #2d4352;background:#0d171f}.v31-bridge-labels>div{padding:14px 22px;font-size:.67rem;font-weight:900;letter-spacing:.12em}.v31-bridge-labels .challenge-label{color:#e3838e}.v31-bridge-labels .response-label{color:#65d19b}.v31-bridge-grid{display:grid;grid-template-columns:1fr 70px 1fr}.v31-bridge-cell{padding:24px 24px 25px;min-height:260px}.v31-bridge-cell.challenge{background:linear-gradient(145deg,#1b1116,#100d12);border-left:4px solid #b85d6b}.v31-bridge-cell.response{background:linear-gradient(145deg,#0d1c18,#0a1412);border-right:0;border-left:1px solid #25483b}.v31-bridge-cell .num{font-size:.66rem;font-weight:900;letter-spacing:.12em}.v31-bridge-cell.challenge .num{color:#d87984}.v31-bridge-cell.response .num{color:#5fd29a}.v31-bridge-cell h3{font-size:1.2rem;line-height:1.3;margin:8px 0 10px}.v31-bridge-cell p{font-size:.86rem;line-height:1.65;color:#a5b6c3;margin:0 0 14px}.v31-bridge-link{display:flex;align-items:center;justify-content:center;background:#0b131a;border-left:1px solid #334956;border-right:1px solid #334956;position:relative}.v31-bridge-link span{width:43px;height:43px;border:1px solid #4f7389;border-radius:50%;display:flex;align-items:center;justify-content:center;color:#82c7ee;font-size:1.2rem;background:#10202b;box-shadow:0 8px 25px rgba(0,0,0,.2)}.v31-source-preview{border:1px solid #334a5a;border-radius:11px;overflow:hidden;background:#081018;margin-top:12px}.v31-source-bar{height:29px;background:#101e29;border-bottom:1px solid #2b4150;display:flex;align-items:center;gap:5px;padding:0 9px}.v31-source-dot{width:7px;height:7px;border-radius:50%;background:#547084}.v31-source-domain{font-size:.59rem;color:#71899b;margin-left:5px}.v31-source-body{padding:11px 12px}.v31-source-body strong{display:block;font-size:.66rem;color:#dce8ef}.v31-source-body span{display:block;font-size:.68rem;line-height:1.5;color:#8298a8;margin-top:5px}.v31-source-footer{padding:8px 12px;border-top:1px solid #263b48;color:#70b9ee;font-size:.61rem;font-weight:850}.v31-response-tags{display:flex;flex-wrap:wrap;gap:7px;margin-top:12px}.v31-response-tags span{padding:5px 8px;border:1px solid #315f4b;border-radius:999px;color:#8ed9b1;font-size:.61rem;font-weight:800}.v31-bridge-foot{padding:13px 20px;border-top:1px solid #2d4352;color:#72899a;font-size:.68rem;line-height:1.5;background:#091118}.v31-case-seed{padding:17px 19px;border:1px dashed #385267;border-radius:14px;background:#0a141c;margin:17px 0 20px}.v31-case-seed .label{color:#70b9ee;font-size:.65rem;font-weight:900;letter-spacing:.11em}.v31-case-seed h3{font-size:1.05rem;margin:5px 0}.v31-case-seed p{font-size:.82rem;line-height:1.55;color:#91a5b5;margin:0}.v31-case-seed b{color:#dce8ef}.v31-overview-question{padding:23px 25px;border-left:4px solid #6fb8ed;background:linear-gradient(90deg,#0f1c27,#0b141b);border-top:1px solid #2c4557;border-bottom:1px solid #2c4557;margin:19px 0}.v31-overview-question .label{color:#70b9ee;font-size:.67rem;font-weight:900;letter-spacing:.11em}.v31-overview-question h2{font-size:1.45rem;line-height:1.45;margin:6px 0}.v31-overview-question p{font-size:.85rem;color:#94a8b7;line-height:1.6;margin:0}.v31-overview-map{display:grid;grid-template-columns:repeat(4,1fr);gap:0;border:1px solid #2d4352;border-radius:16px;overflow:hidden;margin:20px 0}.v31-overview-map>div{padding:18px;border-right:1px solid #2d4352;background:#0c151d}.v31-overview-map>div:last-child{border-right:0}.v31-overview-map span{display:block;color:#668eab;font-size:.62rem;font-weight:900;letter-spacing:.1em}.v31-overview-map b{display:block;font-size:.9rem;margin-top:6px}.v31-overview-map small{display:block;color:#8297a8;font-size:.72rem;line-height:1.5;margin-top:4px}.v31-case-start-neutral{margin-top:12px;padding:12px 13px;border-top:1px solid #273746;background:#0a1118}.v31-case-start-neutral span{display:block;color:#64839b;font-size:.57rem;font-weight:900;letter-spacing:.09em}.v31-case-start-neutral b{display:block;font-size:.75rem;margin-top:4px}.v31-case-start-neutral small{display:block;color:#8093a4;font-size:.65rem;margin-top:3px}

/* ============================================================
   V28 — CLARITY / PROCESSING / TECHNICAL DEPTH OVERRIDES
   ============================================================ */
.v28-home-audience{display:grid;grid-template-columns:1.25fr .75fr;gap:24px;margin:28px 0;padding:30px;border:1px solid #385b73;border-radius:20px;background:linear-gradient(145deg,#102330,#0b141c)}
.v28-home-audience h2{font-size:1.75rem;margin:7px 0 10px}.v28-home-audience p{font-size:1rem;line-height:1.75;color:#aebfcd}.v28-audience-grid{display:grid;grid-template-columns:1fr 1fr;gap:12px}.v28-audience-card{padding:16px;border:1px solid #294557;border-radius:13px;background:#0a151e}.v28-audience-card b{display:block;font-size:.98rem}.v28-audience-card span{display:block;color:#91a6b5;font-size:.82rem;line-height:1.5;margin-top:5px}
.v28-home-contract{display:grid;grid-template-columns:1fr 1fr;gap:0;margin:25px 0;border:1px solid #2e4a5e;border-radius:18px;overflow:hidden;background:#0b151d}.v28-contract{padding:27px 29px;min-height:260px}.v28-contract:first-child{border-right:1px solid #2e4a5e}.v28-contract h3{font-size:1.3rem;margin:6px 0 14px}.v28-contract ul{margin:0;padding-left:20px}.v28-contract li{font-size:.95rem;line-height:1.75;color:#b0c0cd;margin:5px 0}.v28-contract .tag{display:inline-block;padding:5px 9px;border:1px solid #35566d;border-radius:999px;color:#70b9ee;font-size:.68rem;font-weight:900;letter-spacing:.08em}
.v28-knowledge{margin:25px 0;padding:28px;border:1px solid #304b5d;border-radius:18px;background:#0c161f}.v28-knowledge-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:14px;margin-top:17px}.v28-knowledge-card{padding:17px;border-top:2px solid #315a78;background:#0a131b}.v28-knowledge-card b{display:block;font-size:.9rem}.v28-knowledge-card span{display:block;color:#94a8b7;font-size:.82rem;line-height:1.55;margin-top:6px}.v28-not-needed{margin-top:17px;color:#83d6ac;font-weight:700;font-size:.88rem}
.v28-processing-trace{margin:28px 0;border:1px solid #36566b;border-radius:18px;background:#0b151e;overflow:hidden}.v28-trace-head{padding:22px 25px;border-bottom:1px solid #294253;background:#0e1c27}.v28-trace-head span{display:block;color:#70b9ee;font-size:.72rem;font-weight:900;letter-spacing:.13em}.v28-trace-head b{display:block;font-size:1.15rem;margin-top:6px}.v28-trace-row{display:grid;grid-template-columns:58px 1fr;gap:17px;padding:16px 22px;border-bottom:1px solid #213442}.v28-trace-row:last-child{border-bottom:0}.v28-trace-num{width:36px;height:36px;border-radius:50%;border:1px solid #4b7593;display:flex;align-items:center;justify-content:center;color:#72b9ff;font-weight:900;font-size:.72rem}.v28-trace-row span{display:block;color:#5f94ba;font-size:.66rem;font-weight:900;letter-spacing:.1em}.v28-trace-row b{display:block;font-size:.96rem;margin:3px 0}.v28-trace-row small{display:block;color:#96a9b8;font-size:.84rem;line-height:1.5}
.v28-formula-card{padding:27px 29px;border:1px solid #3a5d74;border-radius:18px;background:linear-gradient(145deg,#112431,#0b151e)}.v28-formula{font-family:Consolas,monospace;font-size:1.12rem;line-height:1.8;color:#e9f3f8;background:#081018;border:1px solid #243e51;border-radius:12px;padding:17px;margin:14px 0}.v28-formula-note{font-size:.88rem;line-height:1.65;color:#9eb1c0}.v28-score-hero{display:flex;align-items:flex-end;justify-content:space-between;gap:20px;margin:20px 0;padding:24px 28px;border:1px solid #42647a;border-radius:17px;background:#0c1822}.v28-score-hero .score{font-size:4.1rem;font-weight:900;line-height:.95}.v28-score-hero .score small{font-size:1rem;color:#76b7e4;font-weight:700}.v28-score-hero .risk{font-size:1.1rem;font-weight:900;letter-spacing:.12em}.v28-score-hero p{margin:7px 0 0;color:#9fb2c0;font-size:.88rem}.v28-band-row{display:grid;grid-template-columns:repeat(4,1fr);gap:8px;margin-top:15px}.v28-band{padding:11px;border:1px solid #294254;border-radius:10px;text-align:center;color:#9eb1c0;font-size:.72rem}.v28-band.active{border-color:#69b8ea;background:#102638;color:#e7f3fa;font-weight:800}
.v28-ai-pipeline{display:grid;grid-template-columns:1.2fr .35fr 1fr .35fr 1.05fr;align-items:center;gap:12px;margin:25px 0}.v28-ai-box{min-height:155px;padding:19px;border:1px solid #304b5d;border-radius:15px;background:#0c1720}.v28-ai-box span{display:block;color:#70b9ee;font-size:.68rem;font-weight:900;letter-spacing:.1em}.v28-ai-box b{display:block;font-size:1.05rem;margin:7px 0}.v28-ai-box p{color:#91a6b5;font-size:.82rem;line-height:1.55;margin:0}.v28-ai-arrow{text-align:center;color:#6eb8ea;font-size:1.6rem;font-weight:900}.v28-ai-vector{display:grid;grid-template-columns:1fr 1fr;gap:7px;margin-top:10px}.v28-ai-vector div{padding:6px 8px;border:1px solid #253d4d;border-radius:7px;color:#b6c6d0;font-size:.7rem}.v28-ai-output{padding:8px 10px;margin-top:10px;border-left:2px solid #67b9ed;background:#0a141c;color:#e6f1f7;font-weight:800;font-size:.84rem}
.v28-plan-depth{display:grid;grid-template-columns:repeat(3,1fr);gap:14px;margin:23px 0}.v28-depth-card{padding:24px;border:1px solid #314d60;border-radius:17px;background:#0c1720;min-height:250px}.v28-depth-card.active{border-color:#68b8ea;background:linear-gradient(145deg,#102431,#0b151d)}.v28-depth-card .level{color:#70b9ee;font-size:.7rem;font-weight:900;letter-spacing:.12em}.v28-depth-card h3{font-size:1.25rem;margin:7px 0}.v28-depth-card p,.v28-depth-card li{font-size:.88rem;line-height:1.65;color:#9fb1c0}.v28-depth-card ul{padding-left:19px}.v28-tech-spec{margin-top:18px;padding:20px;border:1px solid #294557;border-radius:14px;background:#09131b}.v28-tech-spec-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:10px}.v28-tech-spec-grid div{padding:10px;border-bottom:1px solid #223746}.v28-tech-spec-grid span{display:block;color:#648eab;font-size:.62rem;font-weight:900;letter-spacing:.08em}.v28-tech-spec-grid b{display:block;font-size:.84rem;margin-top:4px;overflow-wrap:anywhere}
.v28-sim-ready{padding:27px 30px;border:1px solid #42647b;border-left:5px solid #69b8ea;border-radius:18px;background:linear-gradient(145deg,#102330,#0b151e);margin:23px 0}.v28-sim-ready h2{font-size:1.65rem;margin:6px 0 9px}.v28-sim-ready p{font-size:1rem;line-height:1.75;color:#aabcca;margin:0}.v28-sim-result{padding:29px 31px!important}.v28-sim-result h2{font-size:2rem!important}.v28-sim-result p{font-size:1.08rem!important;line-height:1.8!important}.v28-sim-result-meta{min-width:185px!important}.v28-sim-result-meta b{font-size:2.5rem!important}.v28-validation-grid{display:grid;grid-template-columns:1.35fr .65fr;gap:24px;margin:18px 0 28px}.v28-validation-list{border:1px solid #2d4658;border-radius:16px;overflow:hidden;background:#0b151d}.v28-validation-item{display:grid;grid-template-columns:48px 1fr;gap:10px;padding:18px 20px;border-bottom:1px solid #253b4a}.v28-validation-item:last-child{border-bottom:0}.v28-validation-item .num{color:#70b9ee;font-weight:900}.v28-validation-item b{font-size:.98rem}.v28-validation-item span{display:block;color:#92a6b5;font-size:.82rem;line-height:1.55;margin-top:3px}.v28-validation-help{padding:24px;border-left:3px solid #68b8ea;background:#0c1822}.v28-validation-help h3{font-size:1.18rem;margin:5px 0 10px}.v28-validation-help p{font-size:.94rem;line-height:1.75;color:#9fb1c0}
.v28-conclusion{margin:30px 0;border:1px solid #41647b;border-radius:20px;background:linear-gradient(145deg,#102431,#0b151e);overflow:hidden}.v28-conclusion-head{padding:25px 29px;border-bottom:1px solid #2d4758}.v28-conclusion-head span{color:#70b9ee;font-size:.72rem;font-weight:900;letter-spacing:.13em}.v28-conclusion-head h2{font-size:1.7rem;line-height:1.35;margin:7px 0 0}.v28-conclusion-grid{display:grid;grid-template-columns:repeat(4,1fr)}.v28-conclusion-cell{padding:22px;border-right:1px solid #2a4353;min-height:165px}.v28-conclusion-cell:last-child{border-right:0}.v28-conclusion-cell span{display:block;color:#6ea9d2;font-size:.66rem;font-weight:900;letter-spacing:.1em}.v28-conclusion-cell b{display:block;font-size:1rem;line-height:1.45;margin:8px 0}.v28-conclusion-cell p,.v28-conclusion-cell li{font-size:.84rem;line-height:1.6;color:#9eb1bf}.v28-conclusion-cell ul{padding-left:18px;margin:6px 0}.v28-bottom-line{padding:22px 29px;border-top:1px solid #2d4758;background:#09131b}.v28-bottom-line b{font-size:1rem}.v28-bottom-line span{display:block;color:#70b9ee;font-size:.66rem;font-weight:900;letter-spacing:.1em;margin-bottom:5px}
.v28-scroll-safe{overflow-wrap:anywhere;word-break:normal}.v28-smallfix{font-size:1rem!important;line-height:1.8!important}.v31-important{font-size:1rem!important;line-height:1.7!important}.v19-finding h2{font-size:1.45rem!important;line-height:1.45!important}.v27-section p,.v27-chart-card p{font-size:1.02rem!important}.v19-check,.v19-conflict{font-size:.94rem!important;line-height:1.7!important;padding:15px 0!important}.v19-table-caption h3{font-size:1.3rem!important}.v19-table-caption p{font-size:.86rem!important}.v19-road-step b{font-size:.95rem!important}.v19-road-step p{font-size:.82rem!important}.v19-gate b{font-size:.9rem!important;line-height:1.55!important}
@media(max-width:1050px){.v28-home-audience,.v28-home-contract{grid-template-columns:1fr}.v28-contract:first-child{border-right:0;border-bottom:1px solid #2e4a5e}.v28-knowledge-grid,.v28-plan-depth{grid-template-columns:1fr}.v28-ai-pipeline{grid-template-columns:1fr}.v28-ai-arrow{transform:rotate(90deg)}.v28-conclusion-grid{grid-template-columns:1fr 1fr}.v28-conclusion-cell:nth-child(2){border-right:0}.v28-conclusion-cell:nth-child(n+3){border-top:1px solid #2a4353}.v28-validation-grid{grid-template-columns:1fr}.v28-tech-spec-grid{grid-template-columns:1fr 1fr}}
@media(max-width:1050px){.v31-audience,.v31-io{grid-template-columns:1fr}.v31-audience-grid,.v31-knowledge-map{grid-template-columns:1fr 1fr}.v31-io-side.input,.v31-io-side.output{border:0}.v31-io-side.input{border-bottom:1px solid #2e4a5e}.v31-io-side.output{border-top:1px solid #2e4a5e}.v31-io-engine{min-height:145px}.v31-bridge-labels,.v31-bridge-grid{grid-template-columns:1fr}.v31-bridge-labels>div:nth-child(2),.v31-bridge-link{display:none}.v31-bridge-cell.response{border-left:4px solid #48bd88;border-top:1px solid #315846}.v31-bridge-cell.challenge{border-left:4px solid #b85d6b}.v31-overview-map{grid-template-columns:1fr 1fr}.v31-overview-map>div:nth-child(2){border-right:0}.v31-overview-map>div:nth-child(n+3){border-top:1px solid #2d4352}}
@media(max-width:650px){.v31-audience-grid,.v31-knowledge-map,.v31-overview-map{grid-template-columns:1fr}.v31-overview-map>div{border-right:0;border-top:1px solid #2d4352}.v31-overview-map>div:first-child{border-top:0}}

/* V35 TRACE evidence surfaces */
.v35-trace-answer{display:grid;grid-template-columns:1.45fr .75fr;gap:18px;margin:18px 0 14px;padding:18px 20px;border:1px solid #365b73;border-radius:15px;background:linear-gradient(135deg,#0d202c,#09151d);align-items:center}
/* TRACE readability pass — preserve layout, increase evidence legibility */
.v35-trace-answer{padding:20px 22px!important}
.v35-trace-answer span,.v35-trace-kpi span,.v35-trace-readout .eyebrow,.v35-primary-path span,.v35-trace-section span,.v35-trace-handoff span{font-size:.70rem!important;letter-spacing:.13em!important}
.v35-trace-answer h3{font-size:1.20rem!important;line-height:1.48!important}
.v35-trace-answer small{font-size:.82rem!important;line-height:1.62!important}
.v35-trace-kpi{padding:16px 16px!important;min-height:100px!important}
.v35-trace-kpi b{font-size:1.22rem!important}
.v35-trace-kpi small{font-size:.74rem!important;line-height:1.5!important}
.v35-trace-readout{padding:20px!important}
.v35-trace-readout h3{font-size:1.18rem!important;line-height:1.35!important}
.v35-trace-line{font-size:.84rem!important;padding:10px 0!important}
.v35-trace-context span{font-size:.68rem!important}
.v35-trace-context b{font-size:.82rem!important;line-height:1.5!important}
.v35-trace-context small{font-size:.76rem!important;line-height:1.55!important}
.v35-primary-path{padding:17px 19px!important}
.v35-primary-path b{font-size:1rem!important;line-height:1.55!important}
.v35-primary-path small{font-size:.76rem!important;line-height:1.5!important}
.v35-trace-section h3{font-size:1.16rem!important;line-height:1.4!important}
.v35-trace-section p{font-size:.82rem!important;line-height:1.6!important}
.v35-trace-handoff>div{padding:18px 20px!important}
.v35-trace-handoff b{font-size:.98rem!important}
.v35-trace-handoff small{font-size:.78rem!important;line-height:1.6!important}
.v35-trace-answer span,.v35-trace-kpi span,.v35-trace-readout .eyebrow,.v35-primary-path span,.v35-trace-section span,.v35-trace-handoff span{display:block;color:#70b9ee;font-size:.62rem;font-weight:900;letter-spacing:.12em}.v35-trace-answer h3{margin:6px 0 0;font-size:1.12rem;line-height:1.42}.v35-trace-answer small{display:block;color:#92a8b8;line-height:1.55;font-size:.72rem}.v35-trace-kpis{display:grid;grid-template-columns:repeat(5,1fr);border:1px solid #294758;border-radius:12px;background:#09151d;margin:0 0 18px;overflow:hidden}.v35-trace-kpi{padding:14px 15px;min-height:92px}.v35-trace-kpi+.v35-trace-kpi{border-left:1px solid #294758}.v35-trace-kpi b{display:block;font-size:1.15rem;margin-top:5px}.v35-trace-kpi small{display:block;color:#879eae;font-size:.67rem;line-height:1.4;margin-top:3px}.v35-trace-readout{border:1px solid #2f5064;border-radius:15px;background:#0a151d;padding:18px 18px 16px}.v35-trace-readout h3{font-size:1.08rem;margin:5px 0 12px}.v35-trace-line{display:flex;justify-content:space-between;gap:12px;padding:8px 0;border-top:1px solid #203845;font-size:.75rem}.v35-trace-line b{color:#7998aa;font-weight:800}.v35-trace-line span{text-align:right;color:#dce9ef}.v35-trace-context{margin-top:12px;padding:12px;border:1px solid #274556;border-radius:10px;background:#081119}.v35-trace-context span{color:#68b2df;font-size:.6rem;font-weight:900;letter-spacing:.1em}.v35-trace-context b{display:block;margin-top:5px;font-size:.73rem;line-height:1.45}.v35-trace-context small{display:block;color:#8098a8;line-height:1.45;margin-top:5px}.v35-primary-path{margin:16px 0 20px;padding:15px 17px;border-left:3px solid #5fa8cf;border-top:1px solid #294758;border-right:1px solid #294758;border-bottom:1px solid #294758;border-radius:0 11px 11px 0;background:#09151d}.v35-primary-path b{display:block;font-size:.9rem;margin-top:5px;line-height:1.5}.v35-primary-path small{display:block;color:#8199a8;font-size:.68rem;margin-top:4px}.v35-trace-section{margin:22px 0 10px}.v35-trace-section h3{margin:5px 0 3px;font-size:1.05rem}.v35-trace-section p{margin:0;color:#839aaa;font-size:.73rem;line-height:1.5}.v35-trace-handoff{display:grid;grid-template-columns:1fr 1fr;margin:20px 0;border:1px solid #31536a;border-radius:14px;background:#0a161f}.v35-trace-handoff>div{padding:16px 18px}.v35-trace-handoff>div+div{border-left:1px solid #294758}.v35-trace-handoff b{display:block;font-size:.88rem;margin-top:5px}.v35-trace-handoff small{display:block;color:#8ca1af;font-size:.69rem;line-height:1.5;margin-top:4px}@media(max-width:1000px){.v35-trace-answer{grid-template-columns:1fr}.v35-trace-kpis{grid-template-columns:1fr 1fr}.v35-trace-kpi:nth-child(3){border-left:0;border-top:1px solid #294758}.v35-trace-kpi:nth-child(n+4){border-top:1px solid #294758}.v35-trace-handoff{grid-template-columns:1fr}.v35-trace-handoff>div+div{border-left:0;border-top:1px solid #294758}}@media(max-width:650px){.v35-trace-kpis{grid-template-columns:1fr}.v35-trace-kpi+.v35-trace-kpi{border-left:0;border-top:1px solid #294758}.v35-trace-line{flex-direction:column}.v35-trace-line span{text-align:left}}

/* ==========================================================
   SIMULATION THEATRE — controlled comparative migration view
   ========================================================== */
.v41-sim-shell{border:1px solid #24465a;border-radius:22px;background:linear-gradient(145deg,#071018 0%,#0b1722 48%,#071018 100%);padding:22px;position:relative;overflow:hidden;box-shadow:0 0 0 1px rgba(66,185,255,.04),0 18px 55px rgba(0,0,0,.28)}
.v41-sim-shell:before{content:"";position:absolute;inset:0;background:linear-gradient(rgba(72,174,224,.025) 1px,transparent 1px),linear-gradient(90deg,rgba(72,174,224,.025) 1px,transparent 1px);background-size:28px 28px;pointer-events:none}
.v41-sim-top,.v41-sim-grid,.v41-sim-timeline,.v41-sim-bottom{position:relative;z-index:1}
.v41-sim-top{display:grid;grid-template-columns:1.55fr .75fr;gap:18px;align-items:stretch}
.v41-sim-kicker{color:#68c9ff;font-size:.62rem;font-weight:900;letter-spacing:.16em}.v41-sim-top h2{font-size:1.75rem;margin:7px 0 6px}.v41-sim-top p{color:#8fa8b8;line-height:1.55;margin:0;max-width:760px;font-size:.8rem}
.v41-sim-asset{border:1px solid #31536a;border-radius:16px;background:linear-gradient(135deg,rgba(15,35,49,.9),rgba(8,17,25,.9));padding:17px}.v41-sim-asset span{display:block;color:#7898aa;font-size:.58rem;letter-spacing:.13em;font-weight:900}.v41-sim-asset b{display:block;font-size:1.08rem;margin-top:5px}.v41-sim-asset small{display:block;color:#8399a8;margin-top:4px;line-height:1.45}
.v41-sim-flow{display:flex;gap:8px;align-items:center;flex-wrap:wrap;margin-top:16px}.v41-sim-chip{border:1px solid #29485b;background:#0a1720;border-radius:999px;padding:7px 11px;color:#a9bfcc;font-size:.64rem}.v41-sim-chip.active{border-color:#42baff;color:#dff5ff;box-shadow:0 0 18px rgba(66,186,255,.12)}.v41-sim-arrow{color:#4f91b7;font-size:.8rem}
.v41-sim-notice{margin-top:15px;border:1px solid #314b5b;border-radius:12px;background:rgba(7,16,23,.72);padding:10px 13px;color:#879eae;font-size:.69rem;line-height:1.5}.v41-sim-notice b{color:#d5e5ed}
.v41-sim-timeline{margin:20px 0 16px;border:1px solid #203c4e;border-radius:15px;background:#07121a;padding:13px 14px}.v41-timeline-line{display:grid;grid-template-columns:repeat(6,1fr);gap:0;position:relative}.v41-timeline-line:before{content:"";position:absolute;top:13px;left:8%;right:8%;height:1px;background:linear-gradient(90deg,#28546c,#3a8fb9,#28546c)}.v41-step{position:relative;text-align:center;cursor:pointer;z-index:1}.v41-step .dot{margin:0 auto 7px;width:27px;height:27px;border-radius:50%;border:1px solid #31556b;background:#091720;display:flex;align-items:center;justify-content:center;color:#7091a4;font-size:.6rem;font-weight:900;transition:.2s}.v41-step.active .dot{border-color:#57c9ff;background:#0d2b3b;color:#e5f8ff;box-shadow:0 0 20px rgba(70,195,255,.25)}.v41-step.done .dot{border-color:#3e8eac;color:#b9eaff}.v41-step b{display:block;font-size:.63rem}.v41-step small{display:block;color:#6f8797;font-size:.53rem;margin-top:3px}.v41-sim-grid{display:grid;grid-template-columns:1fr 1fr;gap:14px}
.v41-side{border:1px solid #244052;border-radius:17px;background:linear-gradient(180deg,#0b1720,#071119);overflow:hidden}.v41-side.unprepared{border-color:#4c3e3c}.v41-side.planned{border-color:#28566a}.v41-side-head{padding:14px 16px;border-bottom:1px solid #213744;display:flex;justify-content:space-between;gap:12px;align-items:center}.v41-side-head span{font-size:.58rem;letter-spacing:.13em;font-weight:900;color:#7d9aaa}.v41-side-head b{font-size:.78rem}.v41-side-head em{font-style:normal;font-size:.55rem;border:1px solid #35596d;border-radius:999px;padding:4px 7px;color:#86b8d2}.v41-side.unprepared .v41-side-head em{border-color:#70504a;color:#d2a59b}.v41-graph-wrap{padding:5px 7px 0;background:radial-gradient(circle at 50% 50%,rgba(39,134,182,.07),transparent 55%)}
.v41-side-caption{padding:11px 15px 15px;color:#8399a8;font-size:.67rem;line-height:1.5;min-height:58px}.v41-side-caption b{color:#d8e7ef}.v41-side-caption strong{color:#62c7f7}
.v41-sim-bottom{display:grid;grid-template-columns:1.25fr .75fr;gap:14px;margin-top:14px}.v41-finding,.v41-log{border:1px solid #244052;border-radius:16px;background:#08131b;padding:15px}.v41-finding .eyebrow,.v41-log .eyebrow{color:#67c8fb;font-size:.57rem;font-weight:900;letter-spacing:.14em}.v41-finding h3{font-size:1.05rem;margin:7px 0 5px}.v41-finding p{color:#8da2b1;font-size:.72rem;line-height:1.55;margin:0}.v41-finding .evidence{display:flex;flex-wrap:wrap;gap:7px;margin-top:11px}.v41-finding .evidence span{border:1px solid #28485a;border-radius:8px;padding:5px 7px;color:#9bb5c4;font-size:.57rem;background:#0b1a24}.v41-log-row{display:grid;grid-template-columns:58px 52px 1fr;gap:7px;padding:6px 0;border-bottom:1px solid #172c39;font-family:Consolas,monospace;font-size:.56rem}.v41-log-row:last-child{border-bottom:0}.v41-log-row time{color:#50748a}.v41-log-row b{color:#67c8fb}.v41-log-row span{color:#91a6b4;line-height:1.35}
.v41-controls{display:flex;justify-content:center;align-items:center;gap:8px;flex-wrap:wrap;margin:14px 0 3px;position:relative;z-index:2}.v41-controls button{border:1px solid #31576c;background:#0a1720;color:#c9dce6;border-radius:9px;padding:8px 13px;font-size:.67rem;font-weight:800}.v41-controls .primary{border-color:#4bbcf1;background:linear-gradient(135deg,#0d3448,#0b2533);box-shadow:0 0 18px rgba(53,184,243,.1)}
.v41-compare{margin-top:14px;border:1px solid #263f50;border-radius:14px;background:#071119;padding:11px 13px;display:flex;gap:14px;align-items:center;justify-content:space-between}.v41-compare b{font-size:.72rem}.v41-compare span{color:#7f96a5;font-size:.62rem}.v41-compare .same{color:#67c8fb}
@media(max-width:1000px){.v41-sim-top,.v41-sim-grid,.v41-sim-bottom{grid-template-columns:1fr}.v41-timeline-line{grid-template-columns:repeat(3,1fr);row-gap:12px}.v41-timeline-line:before{display:none}}
@media(prefers-reduced-motion:reduce){.v41-step .dot{transition:none}.v41-sim-shell *{scroll-behavior:auto}}

/* ============================================================
   SIMULATION V2 — focused state-transition decision surface
   ============================================================ */
.v42-sim{border:1px solid #294657;border-radius:18px;background:#09131b;overflow:hidden;margin:8px 0 18px}
.v42-head{padding:24px 26px 20px;border-bottom:1px solid #223845;background:#0a151d}
.v42-kicker{color:#68c8f5;font-size:.61rem;font-weight:900;letter-spacing:.16em}
.v42-head h2{font-size:1.65rem;line-height:1.25;margin:7px 0 7px;color:#eef6fa}
.v42-head p{margin:0;max-width:900px;color:#91a7b5;font-size:.82rem;line-height:1.6}
.v42-transition{display:flex;align-items:center;gap:9px;flex-wrap:wrap;margin-top:16px}
.v42-asset{border:1px solid #315568;background:#0b1a23;border-radius:9px;padding:8px 11px;color:#dbeaf1;font-size:.68rem;font-weight:800}
.v42-asset.current{border-color:#3c9ac4}.v42-arrow{color:#5f9bb8;font-size:.9rem}.v42-meta{color:#8ca4b3;font-size:.67rem}
.v42-contract{margin:0 26px 18px;border:1px solid #2a4555;border-radius:10px;background:#0b171f;padding:10px 12px;color:#879eac;font-size:.68rem;line-height:1.5}.v42-contract b{color:#d5e4eb}
.v42-strategy{padding:0 26px 18px}.v42-strategy-label{color:#7893a3;font-size:.59rem;font-weight:900;letter-spacing:.13em;margin-bottom:8px}
.v42-strategy-grid{display:grid;grid-template-columns:1fr 1fr;gap:9px}
.v42-strategy-card{border:1px solid #294454;border-radius:11px;background:#0a151d;padding:11px 13px;min-height:74px}.v42-strategy-card.active{border-color:#3fa9d8;background:#0b1b25;box-shadow:inset 3px 0 #42b9ec}.v42-strategy-card .tag{font-size:.56rem;color:#718e9f;font-weight:900;letter-spacing:.1em}.v42-strategy-card b{display:block;font-size:.77rem;margin:4px 0}.v42-strategy-card small{color:#8198a7;font-size:.64rem;line-height:1.4}
.v42-steps{display:grid;grid-template-columns:repeat(6,1fr);border-top:1px solid #223845;border-bottom:1px solid #223845;background:#08131a}
.v42-step{padding:12px 8px 11px;text-align:center;position:relative}.v42-step+.v42-step{border-left:1px solid #1c303c}.v42-step .num{display:block;color:#607f90;font-size:.55rem;font-weight:900;letter-spacing:.08em}.v42-step b{display:block;color:#91a9b7;font-size:.62rem;margin-top:4px}.v42-step.active{background:#0b1b24}.v42-step.active .num,.v42-step.active b{color:#66c9f5}.v42-step.done .num{color:#4c91ad}.v42-step.done b{color:#b1c4ce}.v42-step small{display:block;color:#587484;font-size:.49rem;line-height:1.25;margin-top:3px}.v42-step.active small{color:#7da8ba}
.v42-main{display:grid;grid-template-columns:minmax(0,1.55fr) minmax(300px,.85fr);gap:14px;margin:14px 0}
.v42-panel{border:1px solid #263f4d;border-radius:15px;background:#08131a;overflow:hidden}.v42-panel-head{padding:13px 15px;border-bottom:1px solid #1f3541;display:flex;justify-content:space-between;align-items:center;gap:12px}.v42-panel-head span{color:#6b91a3;font-size:.57rem;font-weight:900;letter-spacing:.13em}.v42-panel-head b{font-size:.76rem;color:#dbe8ee}.v42-panel-head em{font-style:normal;font-size:.56rem;color:#79c5e8;border:1px solid #315b70;border-radius:999px;padding:4px 7px}
.v42-graph{padding:0;background:#071119}.v42-readout{padding:16px}.v42-finding-kicker{color:#69c9f5;font-size:.57rem;font-weight:900;letter-spacing:.13em}.v42-readout h3{font-size:1.12rem;line-height:1.35;margin:6px 0}.v42-readout p{color:#91a6b4;font-size:.72rem;line-height:1.58;margin:0}.v42-metrics{display:grid;grid-template-columns:repeat(2,1fr);gap:7px;margin-top:13px}.v42-metric{border:1px solid #223c4b;border-radius:9px;padding:9px 10px;background:#0a171f}.v42-metric span{display:block;color:#67899a;font-size:.53rem;font-weight:900;letter-spacing:.08em}.v42-metric b{display:block;font-size:.9rem;margin-top:4px}.v42-section-title{margin:15px 0 7px;color:#7895a5;font-size:.57rem;font-weight:900;letter-spacing:.12em}
.v42-gate{display:flex;align-items:flex-start;gap:8px;padding:7px 0;border-top:1px solid #1c303b;font-size:.66rem;line-height:1.4}.v42-gate:first-of-type{border-top:0}.v42-gate .state{width:15px;height:15px;border-radius:50%;border:1px solid #405967;display:flex;align-items:center;justify-content:center;flex:none;font-size:.5rem;margin-top:1px}.v42-gate.ready .state{border-color:#55b8df;color:#65c9f4}.v42-gate.pending .state{border-color:#9b7d46;color:#d6a95f}.v42-gate.conflict .state{border-color:#a75c64;color:#e07b87}.v42-gate span{color:#b4c5ce}.v42-why{margin-top:12px;border-left:2px solid #397f9e;padding:9px 11px;background:#09171f}.v42-why b{display:block;font-size:.64rem;color:#d4e4eb}.v42-why small{display:block;color:#8199a8;font-size:.63rem;line-height:1.5;margin-top:3px}
.v42-delta{display:grid;grid-template-columns:1fr 28px 1fr;margin:0 0 14px;border:1px solid #263f4d;border-radius:13px;background:#08131a;overflow:hidden}.v42-delta-side{padding:13px 15px}.v42-delta-side+.v42-delta-side{border-left:1px solid #223845}.v42-delta-side .label{color:#6b8b9c;font-size:.55rem;font-weight:900;letter-spacing:.12em}.v42-delta-side b{display:block;font-size:.79rem;margin-top:5px}.v42-delta-side small{display:block;color:#849ba9;font-size:.63rem;line-height:1.45;margin-top:3px}.v42-delta-arrow{display:flex;align-items:center;justify-content:center;color:#4f8da9;border-left:1px solid #223845}
.v42-propagation{border:1px solid #263f4d;border-radius:13px;background:#08131a;padding:14px 16px}.v42-propagation h3{font-size:.78rem;margin:0 0 10px}.v42-chain{display:grid;grid-template-columns:repeat(5,1fr);gap:0}.v42-chain div{position:relative;padding:9px 7px;text-align:center;border:1px solid #233d4b;background:#0a171f}.v42-chain div:first-child{border-radius:8px 0 0 8px}.v42-chain div:last-child{border-radius:0 8px 8px 0}.v42-chain div+div{border-left:0}.v42-chain span{display:block;color:#5f8191;font-size:.51rem;font-weight:900;letter-spacing:.07em}.v42-chain b{display:block;color:#b9cad3;font-size:.61rem;margin-top:4px;line-height:1.25}.v42-chain .active{background:#0b1d27;border-color:#34728f}.v42-chain .active b{color:#dcecf2}
.v42-bottom{display:grid;grid-template-columns:1fr .95fr;gap:14px;margin-bottom:14px}.v42-log{border:1px solid #263f4d;border-radius:13px;background:#08131a;padding:14px 16px}.v42-log h3{font-size:.78rem;margin:0 0 8px}.v42-log-row{display:grid;grid-template-columns:54px 58px 1fr;gap:7px;padding:7px 0;border-top:1px solid #1c303b;font-family:Consolas,monospace;font-size:.57rem}.v42-log-row time{color:#52768a}.v42-log-row b{color:#68c8f5}.v42-log-row span{color:#879daa;line-height:1.4}
.v42-decision{border:1px solid #31566a;border-radius:15px;background:#0a1720;padding:18px 20px;margin-bottom:10px}.v42-decision .kicker{color:#68c8f5;font-size:.58rem;font-weight:900;letter-spacing:.14em}.v42-decision h2{font-size:1.2rem;margin:6px 0}.v42-decision p{color:#91a6b4;font-size:.72rem;line-height:1.58;margin:0;max-width:920px}.v42-decision-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:7px;margin-top:13px}.v42-decision-grid div{border:1px solid #243f4d;border-radius:8px;padding:9px;background:#09141c}.v42-decision-grid span{display:block;color:#668697;font-size:.5rem;font-weight:900;letter-spacing:.07em}.v42-decision-grid b{display:block;font-size:.86rem;margin-top:4px}.v42-note{color:#728a99;font-size:.62rem;line-height:1.5;margin-top:10px}

.v42-plain{margin:12px 0 14px;border:1px solid #2a4655;border-radius:11px;background:#0a171f;padding:11px 14px;display:flex;align-items:flex-start;gap:11px}.v42-plain .icon{width:24px;height:24px;border-radius:50%;display:flex;align-items:center;justify-content:center;flex:none;border:1px solid #397f9e;color:#69c9f5;font-size:.62rem;font-weight:900}.v42-plain.warn{border-color:#66512f;background:#17140d}.v42-plain.warn .icon{border-color:#9a7841;color:#d4a75e}.v42-plain b{display:block;font-size:.58rem;letter-spacing:.11em;color:#6d91a2}.v42-plain p{margin:3px 0 0;color:#c2d2da;font-size:.72rem;line-height:1.48}.v42-gatestrip{border:1px solid #263f4d;border-radius:12px;background:#08131a;padding:11px 13px;margin:0 0 14px}.v42-gatestrip-head{display:flex;justify-content:space-between;align-items:center;margin-bottom:8px}.v42-gatestrip-head span{color:#6c8d9e;font-size:.55rem;font-weight:900;letter-spacing:.13em}.v42-gatestrip-head b{font-size:.62rem;color:#a9bdc8}.v42-gates{display:grid;grid-template-columns:repeat(4,1fr);gap:7px}.v42-gatebox{border:1px solid #253e4c;border-radius:8px;background:#0a171f;padding:8px 9px;min-height:50px}.v42-gatebox .state{font-size:.58rem;font-weight:900}.v42-gatebox b{display:block;font-size:.58rem;color:#b7c9d2;margin-top:3px}.v42-gatebox small{display:block;font-size:.5rem;color:#718b9a;margin-top:2px}.v42-gatebox.ready{border-color:#326a83}.v42-gatebox.ready .state{color:#67c8f5}.v42-gatebox.applied{border-color:#326a83;background:#0b1b24}.v42-gatebox.applied .state{color:#69c9f5}.v42-gatebox.warn{border-color:#70582f;background:#17140d}.v42-gatebox.warn .state{color:#d4a75e}.v42-gatebox.pending .state{color:#6e8795}.v42-sequence{border:1px solid #263f4d;border-radius:12px;background:#08131a;padding:12px 14px;margin:14px 0}.v42-sequence h3{font-size:.72rem;margin:0 0 8px}.v42-seqrow{display:grid;grid-template-columns:105px 1fr;gap:10px;align-items:center;padding:7px 0;border-top:1px solid #1b303b}.v42-seqrow:first-of-type{border-top:0}.v42-seqrow>span{font-size:.53rem;font-weight:900;letter-spacing:.08em;color:#718d9d}.v42-seqrow>div{display:flex;align-items:center;gap:5px;flex-wrap:wrap}.v42-seqrow i{font-style:normal;border:1px solid #294554;border-radius:6px;padding:4px 6px;color:#a8bbc5;font-size:.54rem;background:#0a171f}.v42-seqrow i.current{border-color:#397f9e;color:#d8ebf3;background:#0b1d27}.v42-seqrow i.warn{border-color:#70582f;color:#d4a75e;background:#17140d}.v42-mini-arrow{color:#526f7e;font-size:.6rem}.v42-issue{margin-top:10px;border:1px solid #6a532e;border-radius:9px;background:#17140d;padding:9px 10px}.v42-issue b{display:block;color:#d4a75e;font-size:.57rem;letter-spacing:.1em}.v42-issue span{display:block;color:#bfae8b;font-size:.61rem;line-height:1.45;margin-top:3px}.v42-decision.warn{border-color:#6b552f;background:#17140d}.v42-decision.warn .kicker{color:#d4a75e}.v42-decision.warn h2{color:#f0dfbd}.v42-decision.good{border-color:#315f73}
@media(max-width:1050px){.v42-main,.v42-bottom{grid-template-columns:1fr}.v42-chain{grid-template-columns:1fr}.v42-chain div,.v42-chain div:first-child,.v42-chain div:last-child{border-left:1px solid #233d4b;border-radius:0}.v42-chain div:first-child{border-radius:8px 8px 0 0}.v42-chain div:last-child{border-radius:0 0 8px 8px}.v42-steps{grid-template-columns:repeat(3,1fr)}.v42-step:nth-child(4){border-left:0;border-top:1px solid #1c303c}.v42-step:nth-child(5),.v42-step:nth-child(6){border-top:1px solid #1c303c}}
@media(max-width:650px){.v42-strategy-grid,.v42-decision-grid{grid-template-columns:1fr}.v42-steps{grid-template-columns:repeat(2,1fr)}.v42-metrics{grid-template-columns:1fr}.v42-gates{grid-template-columns:repeat(2,1fr)}.v42-seqrow{grid-template-columns:1fr;gap:5px}.v42-transition{align-items:flex-start;flex-direction:column}.v42-delta{grid-template-columns:1fr}.v42-delta-arrow{display:none}.v42-delta-side+.v42-delta-side{border-left:0;border-top:1px solid #223845}}


/* SIMULATION V2.2 — readability, causal clarity and restrained cyber corners */
.v42-sim{position:relative;border-color:#2d5368;background:radial-gradient(circle at 0% 0%,rgba(39,177,235,.13),transparent 25%),radial-gradient(circle at 100% 100%,rgba(92,67,190,.10),transparent 27%),linear-gradient(145deg,#08131c,#09151e 55%,#071018);box-shadow:0 0 0 1px rgba(73,199,241,.035),0 18px 60px rgba(0,0,0,.24)}
.v42-sim:before,.v42-sim:after{content:"";position:absolute;width:150px;height:150px;pointer-events:none;z-index:0;filter:blur(1px)}
.v42-sim:before{left:-70px;top:-70px;background:radial-gradient(circle,rgba(43,193,246,.18),transparent 68%)}
.v42-sim:after{right:-70px;bottom:-70px;background:radial-gradient(circle,rgba(111,76,205,.16),transparent 68%)}
.v42-sim>*{position:relative;z-index:1}
.v42-kicker{font-size:.68rem!important}.v42-head h2{font-size:1.82rem!important}.v42-head p{font-size:.91rem!important;line-height:1.65!important}.v42-asset{font-size:.76rem!important;padding:9px 12px!important}.v42-meta{font-size:.74rem!important}.v42-contract{font-size:.76rem!important;line-height:1.6!important}.v42-strategy-label{font-size:.65rem!important}.v42-strategy-card{padding:13px 15px!important;min-height:82px!important}.v42-strategy-card .tag{font-size:.61rem!important}.v42-strategy-card b{font-size:.86rem!important}.v42-strategy-card small{font-size:.72rem!important}.v42-step .num{font-size:.62rem!important}.v42-step b{font-size:.70rem!important}.v42-step small{font-size:.59rem!important}.v42-plain{padding:13px 15px!important}.v42-plain b{font-size:.64rem!important}.v42-plain p{font-size:.82rem!important;line-height:1.55!important}.v42-gatestrip-head span{font-size:.62rem!important}.v42-gatestrip-head b{font-size:.70rem!important}.v42-gatebox{padding:10px 11px!important;min-height:58px!important}.v42-gatebox b{font-size:.66rem!important}.v42-gatebox small{font-size:.59rem!important}.v42-panel-head span{font-size:.62rem!important}.v42-panel-head b{font-size:.84rem!important}.v42-readout{padding:18px!important}.v42-finding-kicker{font-size:.62rem!important}.v42-readout h3{font-size:1.24rem!important}.v42-readout p{font-size:.80rem!important;line-height:1.62!important}.v42-metric span{font-size:.58rem!important}.v42-metric b{font-size:1rem!important}.v42-section-title{font-size:.62rem!important}.v42-gate{font-size:.75rem!important;padding:9px 0!important}.v42-gate .state{width:18px;height:18px;font-size:.58rem!important}.v42-why{padding:11px 13px!important}.v42-why b{font-size:.68rem!important}.v42-why small{font-size:.72rem!important;line-height:1.55!important}.v42-delta-side .label{font-size:.61rem!important}.v42-delta-side b{font-size:.88rem!important}.v42-delta-side small{font-size:.70rem!important}.v42-propagation h3,.v42-sequence h3,.v42-log h3{font-size:.82rem!important}.v42-chain b{font-size:.68rem!important}.v42-chain span{font-size:.56rem!important}.v42-log-row{font-size:.64rem!important}.v42-decision h2{font-size:1.3rem!important}.v42-decision p{font-size:.80rem!important}.v42-note{font-size:.68rem!important}
</style>
""",unsafe_allow_html=True)

# ============================================================

# HOME
if not st.session_state.analysis_complete:
    st.markdown("<div class='v18-page'>", unsafe_allow_html=True)
    st.markdown("""
    <div class='v20-home-hero'>
      <div class='v18-eyebrow'>NEXORA · CRYPTO-AGILITY INVESTIGATION CONSOLE</div>
      <h1>See what changes before you change the cryptography.</h1>
      <p>NEXORA is a decision-support workbench for understanding cryptographic dependencies before a post-quantum migration. It connects discovery, dependency reasoning, impact interpretation, migration preparation and controlled simulation.</p>
      <div class='v20-home-answer'><span>THE QUESTION NEXORA ANSWERS</span><b>If this cryptographic dependency changes, what else could be affected — and what must be prepared first?</b></div>
      <div class='v20-home-flow'>
        <div><strong>01</strong><b>DISCOVER</b><span>Find what exists</span></div><i>→</i>
        <div><strong>02</strong><b>TRACE</b><span>Follow dependencies</span></div><i>→</i>
        <div><strong>03</strong><b>ASSESS</b><span>Explain impact</span></div><i>→</i>
        <div><strong>04</strong><b>PLAN</b><span>Prepare the sequence</span></div><i>→</i>
        <div><strong>05</strong><b>SIMULATE</b><span>Test the consequence</span></div>
      </div>
    </div>

    <div class='v31-audience'>
      <div class='v31-audience-intro'>
        <div class='v18-eyebrow'>WHO NEXORA IS FOR</div>
        <h2>Different infrastructure roles can use the same evidence trail for different decisions.</h2>
        <p>NEXORA is designed around the people who need to understand the operational consequences of cryptographic change — not around one job title.</p>
        <p><b>AI expertise is not required.</b> The system exposes the evidence, dependency relationships and reasoning stages so the user can inspect how the result was produced.</p>
      </div>
      <div class='v31-audience-grid'>
        <div class='v31-audience-card'><div class='role'>01 · SECURITY ARCHITECT / CYBERSECURITY</div><h3>Understand exposure before a cryptographic change.</h3><p>Uses NEXORA to connect cryptographic exposure with affected services and infrastructure consequences.</p></div>
        <div class='v31-audience-card'><div class='role'>02 · CRYPTOGRAPHY / PKI ENGINEER</div><h3>Trace certificates, algorithms and trust relationships.</h3><p>Uses the inventory and ACDKG to see what owns, presents and depends on a cryptographic asset.</p></div>
        <div class='v31-audience-card'><div class='role'>03 · NETWORK / INFRASTRUCTURE ENGINEER</div><h3>See how protocol and service paths can be affected.</h3><p>Uses dependency paths around TLS, SSH, VPN, services, libraries and downstream applications.</p></div>
        <div class='v31-audience-card'><div class='role'>04 · PQC MIGRATION TEAM</div><h3>Turn inventory into migration preparation.</h3><p>Uses impact evidence, preparation gates and controlled what-if analysis to support migration planning.</p></div>
      </div>
    </div>

    <div class='v31-io'>
      <div class='v31-io-side input'><span class='tag'>WHAT GOES INTO NEXORA</span><h3>Evidence from the environment</h3><ul><li>Operating-system and service context</li><li>Applications, processes and infrastructure components</li><li>Cryptographic assets, certificates and algorithms</li><li>Protocols, libraries and authentication relationships</li><li>Dependency and trust relationships</li></ul></div>
      <div class='v31-io-engine'><div class='v31-engine-box'><span>NEXORA ENGINE</span><b>Evidence → Reasoning</b><small>ACDKG + impact logic + controlled AI effort signal</small></div></div>
      <div class='v31-io-side output'><span class='tag'>WHAT NEXORA GIVES BACK</span><h3>A decision trail</h3><ul><li>Cryptographic inventory</li><li>ACDKG consequence paths</li><li>Impact and CMIS evidence</li><li>AI-assisted migration-effort signal</li><li>Dependency-aware preparation sequence</li><li>Controlled migration simulation</li></ul></div>
    </div>

    <div class='v28-knowledge'>
      <div class='v18-eyebrow'>WHAT THE USER SHOULD ALREADY UNDERSTAND</div>
      <h2 style='margin:6px 0 0;font-size:1.6rem'>Enough engineering context to interpret the evidence — not to build NEXORA.</h2>
      <div class='v31-knowledge-map'>
        <div class='v31-knowledge-card'><div class='level'>FOUNDATION</div><h3>Systems + networks</h3><p>Operating systems, services, applications, basic networking, TLS/HTTPS and SSH.</p></div>
        <div class='v31-knowledge-card'><div class='level'>SECURITY</div><h3>Classical cryptography + PKI</h3><p>RSA, ECC, certificates, PKI, trust relationships and cryptographic libraries.</p></div>
        <div class='v31-knowledge-card'><div class='level'>PQC</div><h3>Migration concepts</h3><p>Basic understanding of ML-KEM, ML-DSA, SLH-DSA and why replacing cryptography affects surrounding systems.</p></div>
      </div>
      <div class='v31-not-needed'>AI/ML expertise is not required to read the investigation output · Quantum-computer implementation is outside this prototype · NEXORA does not execute production cryptographic changes.</div>
    </div>

    <div class='v21-home-propagation'>
      <div class='v21-prop-intro'><span>THE CORE NEXORA IDEA</span><h3>A cryptographic change rarely stays inside the cryptographic object.</h3><p>NEXORA follows the change outward through the owner, protocol, library and dependent applications before proposing a migration sequence.</p></div>
      <div class='v21-prop-chain'><div><b>CRYPTO ASSET</b><span>RSA / ECC / certificate</span></div><i>→</i><div><b>OWNER SERVICE</b><span>Identity / API / VPN</span></div><i>→</i><div><b>PROTOCOL + LIBRARY</b><span>TLS / SSH / OpenSSL</span></div><i>→</i><div><b>DEPENDENT SYSTEMS</b><span>Applications / services</span></div></div>
    </div>

    <div class='v31-bridge'>
      <div class='v31-bridge-head'><div class='eyebrow'>REAL-WORLD STATE → NEXORA RESPONSE</div><h2>Where the migration problem exists — and exactly where this prototype responds.</h2><p>The left side is grounded in current NIST/ENISA material. The right side is deliberately narrower: it describes what NEXORA implements in its controlled academic environment.</p></div>
      <div class='v31-bridge-labels'><div class='challenge-label'>WHAT CURRENTLY EXISTS / THE CHALLENGE</div><div></div><div class='response-label'>WHAT NEXORA DOES ABOUT IT</div></div>
    """, unsafe_allow_html=True)

    bridge_rows=[
      ("01","Cryptographic visibility","NIST's PQC migration project treats cryptographic visibility and a comprehensive inventory as a foundation for migration.","NIST NCCoE · Migration to PQC","pages.nist.gov","NEXORA Discovery","NEXORA turns the controlled environment into a structured infrastructure + cryptographic inventory before an investigation target is selected.",["Infrastructure","Crypto assets","Protocols"]),
      ("02","Algorithm changes cross system boundaries","NIST defines crypto agility across protocols, applications, software, hardware, firmware and infrastructure while preserving security and ongoing operations.","NIST CSWP 39upd1 · Final 29 Jun 2026","csrc.nist.gov","NEXORA ACDKG","NEXORA represents the cryptographic object together with its owner, protocol, library and dependent components so the consequence path can be traced.",["Owner","Protocol","Library","Dependents"]),
      ("03","Inventory alone does not answer migration consequence","NIST's migration work separates visibility/risk management from interoperability and benchmarking, showing that identifying cryptography is only part of the migration journey.","NIST NCCoE · Migration to PQC","pages.nist.gov","NEXORA Trace + Assess","NEXORA traverses ACDKG relationships and combines dependency evidence with project-specific CMIS and a controlled AI effort signal.",["Impact path","CMIS","AI effort"]),
      ("04","PQC standards must be integrated into existing systems","NIST states that products, services and protocols need updates as organizations migrate to the finalized PQC standards.","NIST PQC Project · current migration guidance","csrc.nist.gov","NEXORA Plan","NEXORA treats ML-KEM / ML-DSA / SLH-DSA as migration targets and focuses the prototype on preparation, sequencing and validation rather than implementing new algorithms.",["Preparation","Sequencing","Validation"]),
      ("05","Migration requires testing before real execution","NIST's migration project includes interoperability and benchmarking as a dedicated workstream because replacement must work with surrounding implementations.","NIST NCCoE · Interoperability and Benchmarking","pages.nist.gov","NEXORA Simulate","NEXORA performs a controlled what-if traversal and exposes validation gates without claiming that the real-world change has been executed.",["What-if","Conflicts","Validation gates"]),
    ]
    for num,title,challenge,source,domain,response,resp_text,tags in bridge_rows:
        source_url={
          "NIST NCCoE · Migration to PQC":"https://pages.nist.gov/nccoe-migration-post-quantum-cryptography/",
          "NIST CSWP 39upd1 · Final 29 Jun 2026":"https://csrc.nist.gov/pubs/cswp/39/upd1/considerations-for-achieving-crypto-agility/final",
          "NIST PQC Project · current migration guidance":"https://csrc.nist.gov/projects/post-quantum-cryptography",
          "NIST NCCoE · Interoperability and Benchmarking":"https://pages.nist.gov/nccoe-migration-post-quantum-cryptography/",
        }[source]
        st.markdown(f"""<div class='v31-bridge-grid'>
          <div class='v31-bridge-cell challenge'><div class='num'>CHALLENGE {num}</div><h3>{html.escape(title)}</h3><p>{html.escape(challenge)}</p><div class='v31-source-preview'><div class='v31-source-bar'><span class='v31-source-dot'></span><span class='v31-source-dot'></span><span class='v31-source-dot'></span><span class='v31-source-domain'>{html.escape(domain)}</span></div><div class='v31-source-body'><strong>OFFICIAL SOURCE EVIDENCE</strong><span>{html.escape(source)}</span></div><div class='v31-source-footer'><a href='{html.escape(source_url)}' target='_blank'>Open official source ↗</a></div></div></div>
          <div class='v31-bridge-link'><span>→</span></div>
          <div class='v31-bridge-cell response'><div class='num'>NEXORA RESPONSE {num}</div><h3>{html.escape(response)}</h3><p>{html.escape(resp_text)}</p><div class='v31-response-tags'>{''.join(f"<span>{html.escape(t)}</span>" for t in tags)}</div></div>
        </div>""",unsafe_allow_html=True)
    st.markdown("<div class='v31-bridge-foot'><b>Evidence rule:</b> external statements link to official source material. NEXORA response statements describe this prototype's implemented scope and are not claims that the prototype replaces an enterprise migration program.</div></div>",unsafe_allow_html=True)

    st.markdown("<div class='v20-section-head'><div><span>SELECT AN INVESTIGATION</span><h2>Choose the infrastructure problem NEXORA should investigate.</h2></div><p>Each case is a controlled environment with a different dependency pattern.</p></div>",unsafe_allow_html=True)
    cols=st.columns(3,gap="medium")
    role_paths={
      "E-Commerce Order Management":["Customer Web","Identity","Order API","Order App"],
      "University Learning & Identity":["Student Portal","SSO","Learning API","Records"],
      "Healthcare Operations Platform":["Patient Portal","Identity","Clinical API","Records"]
    }
    for col,name in zip(cols,SCENARIOS):
        pcase=SCENARIOS[name];m=preview_case_metrics(name)
        with col:
            _path_nodes = [html.escape(x) for x in role_paths.get(name, ["Service", "Identity", "Application"])]
            role_path_html = "<span class='v20-path-node'>" + "</span><span class='v20-path-arrow'>→</span><span class='v20-path-node'>".join(_path_nodes) + "</span>"
            st.markdown(f"""<div class='v20-case-card'>
              <div class='v20-case-top'><span class='v20-case-icon'>{pcase['icon']}</span><span>{html.escape(pcase['case'])}</span></div>
              <h3>{html.escape(name)}</h3><p>{html.escape(pcase['summary'])}</p>
              <div class='v20-case-question'><span>INVESTIGATION QUESTION</span><b>What could happen if cryptography protecting {html.escape(pcase['focus'].lower())} needs to change?</b></div>
               <div class='v20-case-path'>{role_path_html}</div>
              <div class='v20-case-metrics'><div><b>{m['components']}</b><span>components</span></div><div><b>{m['assets']}</b><span>crypto assets</span></div><div><b>{m['relationships']}</b><span>ACDKG links</span></div></div>
              <div class='v31-case-start-neutral'><span>CASE MODEL</span><b>Multiple cryptographic assets are present.</b><small>NEXORA does not preselect the user's investigation target.</small></div>
            </div>""",unsafe_allow_html=True)
            if st.button("View case brief  →",key=f"v20_preview_{name}",width="stretch",type="primary"):
                st.session_state.case_preview=name;st.rerun()

    if st.session_state.case_preview:
        name=st.session_state.case_preview;pcase=SCENARIOS[name];tdf,tg,tcomp=build_scenario_data(name);m=preview_case_metrics(name)
        st.markdown("<div class='v20-brief-divider'></div>",unsafe_allow_html=True)
        st.markdown(f"""<div class='v20-case-brief'><div class='v20-brief-main'><div class='v18-eyebrow'>CASE BRIEF · {html.escape(pcase['case'])}</div><h2>{html.escape(name)}</h2><p class='v20-brief-summary'>{html.escape(pcase['summary'])}</p><div class='v20-brief-question'><span>INVESTIGATION QUESTION</span><b>What happens if the cryptography protecting {html.escape(pcase['focus'].lower())} needs to change?</b></div><p class='v20-brief-why'>{html.escape(pcase['why'])}</p></div><div class='v20-brief-evidence'><div><span>MODELED ENVIRONMENT</span><b>{len(tcomp)} components</b></div><div><span>CRYPTOGRAPHIC ASSETS</span><b>{len(tdf)}</b></div><div><span>DEPENDENCY RELATIONSHIPS</span><b>{tg.number_of_edges()}</b></div><div><span>CASE SEED</span><b>Defined for reproducibility</b><small>The seed does not select the user's investigation target.</small></div></div></div>""",unsafe_allow_html=True)
        bc1,bc2=st.columns([1,1],gap="medium")
        with bc1:
            if st.button("Enter this investigation  →",key="v20_enter_case",width="stretch",type="primary"): activate(name);st.rerun()
        with bc2:
            if st.button("Close case brief",key="v20_close_case",width="stretch"): st.session_state.case_preview=None;st.rerun()

    st.markdown("<div class='v20-section-head v20-work-head'><div><span>THE INVESTIGATION MODEL</span><h2>Evidence → interpretation → decision → controlled what-if</h2></div><p>Every stage answers one question and produces the evidence needed by the next stage.</p></div>",unsafe_allow_html=True)
    steps=[("01","DISCOVER","What exists?","Inventory becomes evidence."),("02","TRACE","What depends on it?","ACDKG reveals consequence paths."),("03","ASSESS","Why does it matter?","Risk + CMIS + AI become interpretable evidence."),("04","PLAN","What comes first?","Technical preparation becomes a migration sequence."),("05","SIMULATE","What changes if we replace it?","NEXORA exposes consequence and validation gates.")]
    st.markdown("<div class='v20-home-steps'>"+"".join(f"<div><strong>{n}</strong><b>{title}</b><span>{q}</span><small>{out}</small></div>" for n,title,q,out in steps)+"</div>",unsafe_allow_html=True)
    st.markdown("""<div class='v20-research'><div class='v20-research-head'><div><span>RESEARCH GROUNDING</span><h2>Built around the current PQC migration problem.</h2></div><p>External standards provide context; NEXORA's calculations and ACDKG are project-specific.</p></div><div class='v20-research-grid'><div><b>CRYPTO AGILITY</b><p>Replace or adapt cryptographic algorithms across systems while preserving security and ongoing operations.</p><a href='https://csrc.nist.gov/pubs/cswp/39/upd1/considerations-for-achieving-crypto-agility/final' target='_blank'>NIST CSWP 39upd1 · 2026 ↗</a></div><div><b>CRYPTOGRAPHIC VISIBILITY</b><p>NIST's migration project centers a comprehensive cryptographic inventory and risk-management workstream.</p><a href='https://pages.nist.gov/nccoe-migration-post-quantum-cryptography/' target='_blank'>NIST NCCoE · updated 30 Jun 2026 ↗</a></div><div><b>PQC STANDARDS + MIGRATION</b><p>NIST's principal PQC standards are ML-KEM, ML-DSA and SLH-DSA, and organizations should begin migration work.</p><a href='https://csrc.nist.gov/projects/post-quantum-cryptography' target='_blank'>NIST PQC Project ↗</a></div></div></div>""",unsafe_allow_html=True)
    st.markdown("<div class='v20-boundary'><div><span>PROJECT BOUNDARY</span><h3>Autonomous reasoning and planning inside a controlled prototype.</h3></div><p>NEXORA discovers, models dependencies, reasons over impact, prepares a migration sequence and simulates a proposed change. It does not invent PQC algorithms, claim one laptop represents an enterprise, modify production infrastructure or guarantee a real migration.</p></div>",unsafe_allow_html=True)
    render_footer();st.markdown("</div>",unsafe_allow_html=True);st.stop()

reset_page_scroll_if_needed()

# ============================================================
# V21 SIDEBAR HELPERS — defined before sidebar rendering
# ============================================================
def v21_stage_output(stage, row=None):
    if stage=="OVERVIEW":
        return "Case framed · starting cryptographic dependency identified"
    if stage=="DISCOVERY":
        return f"{len(df)} crypto assets · {len(COMPONENTS)} infrastructure components · {G.number_of_edges()} relationships"
    if stage=="ACDKG":
        return f"{len(impacted_components(row.id))} affected components · depth {max(dependency_depths(row.id).values(),default=0)}" if row is not None else "Select an asset from Discovery"
    if stage=="RISK":
        return f"{row['ML Effort']} effort signal · CMIS {int(row.CMIS)}" if row is not None else "Select an asset from Discovery"
    if stage=="PLAN":
        return f"{len(prepare_asset_decision(row))} preparation gates" if row is not None else "Select an asset from Discovery"
    if stage=="SIMULATE":
        return ("Simulation ready" if not st.session_state.simulation_result else str(st.session_state.simulation_result.get("status","Simulation complete"))) if row is not None else "Select an asset from Discovery"
    return "Evidence available"

# ============================================================
# ACTIVE CASE SIDEBAR
# ============================================================
p=SCENARIOS[st.session_state.selected_environment]
current_stage=st.session_state.stage
note_title,note_text,note_source,note_url=stage_field_note(current_stage)
st.sidebar.markdown("<div class='v20-side-brand'>NEXORA</div>", unsafe_allow_html=True)
st.sidebar.markdown("<div class='v20-side-product'>Crypto-Agility<br>Investigation Console</div>", unsafe_allow_html=True)
st.sidebar.markdown(f"<div class='v20-side-id'>{html.escape(p['case'])} · CONTROLLED LAB</div>", unsafe_allow_html=True)

st.sidebar.markdown("<div class='v20-side-block'>", unsafe_allow_html=True)
st.sidebar.markdown("<div class='v20-side-head'>ACTIVE CASE</div>", unsafe_allow_html=True)
st.sidebar.markdown(f"<div class='v20-side-case'>{html.escape(st.session_state.selected_environment)}</div>", unsafe_allow_html=True)
st.sidebar.caption(p["focus"])
st.sidebar.markdown("</div>", unsafe_allow_html=True)

st.sidebar.markdown("<div class='v20-side-block'>", unsafe_allow_html=True)
st.sidebar.markdown("<div class='v20-side-head'>INVESTIGATION WORKFLOW</div>", unsafe_allow_html=True)
workflow=[("OVERVIEW","Frame the case"),("DISCOVERY","Find what exists"),("ACDKG","Trace dependencies"),("RISK","Assess impact"),("PLAN","Prepare the sequence"),("SIMULATE","Test the consequence")]
for idx,(key,desc) in enumerate(workflow,1):
    cls="active" if key==current_stage else "done" if key in st.session_state.visited_stages else ""
    st.sidebar.markdown(f"<div class='v20-work-step {cls}'><span>{idx:02d}</span><div><b>{html.escape(stage_label(key))}</b><small>{html.escape(desc)}</small></div></div>",unsafe_allow_html=True)
st.sidebar.markdown("</div>", unsafe_allow_html=True)

st.sidebar.markdown("<div class='v20-side-block'>", unsafe_allow_html=True)
st.sidebar.markdown("<div class='v20-side-head'>CASE MODEL</div>", unsafe_allow_html=True)
st.sidebar.markdown(f"<div class='v18-side-metric'><span>Infrastructure</span><b>{len(COMPONENTS)}</b></div>",unsafe_allow_html=True)
st.sidebar.markdown(f"<div class='v18-side-metric'><span>Crypto assets</span><b>{len(df)}</b></div>",unsafe_allow_html=True)
st.sidebar.markdown(f"<div class='v18-side-metric'><span>ACDKG links</span><b>{G.number_of_edges()}</b></div>",unsafe_allow_html=True)
st.sidebar.markdown("</div>", unsafe_allow_html=True)

st.sidebar.markdown(f"""<div class='v20-field-note'>
  <div class='v20-note-label'>{html.escape(note_title)}</div>
  <p>{html.escape(note_text)}</p>
  <div class='v20-note-source'>{html.escape(note_source)}""" + (f" · <a href='{html.escape(note_url)}' target='_blank'>source ↗</a>" if note_url else "") + "</div></div>", unsafe_allow_html=True)

selected_sidebar_row = None
try:
    trace_id=st.session_state.get("trace_asset")
    if trace_id in df.id.tolist():
        selected_sidebar_row = df.loc[df.id == trace_id].iloc[0]
except Exception:
    selected_sidebar_row = None
st.sidebar.markdown(f"<div class='v20-current-stage'><span>CURRENT STAGE PURPOSE</span><b>{html.escape(stage_label(current_stage))}</b><small>{html.escape(stage_question(current_stage))}</small><em>{html.escape(v21_stage_output(current_stage, selected_sidebar_row))}</em></div>",unsafe_allow_html=True)
st.sidebar.markdown("<div class='v21-side-trail'><div class='v20-side-head'>INVESTIGATION TRAIL</div>" + "".join(f"<div class='v21-trail-row {('current' if k==current_stage else 'complete' if k in st.session_state.visited_stages else '')}'><span>{i:02d}</span><b>{html.escape(stage_label(k))}</b><em>{html.escape(v21_stage_output(k, selected_sidebar_row if k in {'ACDKG','RISK','PLAN','SIMULATE'} else None))}</em></div>" for i,k in enumerate([x[0] for x in STAGES],1)) + "</div>",unsafe_allow_html=True)

if st.sidebar.button("← Choose another case", key="v18_change_case", width="stretch"):
    st.session_state.analysis_complete=False
    st.session_state.selected_environment=None
    st.session_state.stage="OVERVIEW"
    st.session_state.visited_stages={"OVERVIEW"}
    st.session_state.case_preview=None
    st.rerun()

# ============================================================
# GLOBAL ACTIVE WORKSPACE
# ============================================================
st.markdown("<div class='v18-page'>", unsafe_allow_html=True)
render_header()
render_context_line()
render_stage_nav(st.session_state.stage)
render_investigation_controls()

# ============================================================
# NEXORA V28 — PRODUCT CLARITY + REAL PROCESSING EVIDENCE
# ============================================================

def v28_probability_figure(row):
    x=feature_row(row)
    probs=MODEL.predict_proba(x)[0]
    labels=list(MODEL.classes_)
    d=pd.DataFrame({"Class":labels,"Probability":probs}).sort_values("Probability")
    fig=go.Figure(go.Bar(x=d["Probability"],y=d["Class"],orientation="h",
                         text=[f"{v:.1%}" for v in d["Probability"]],textposition="auto",
                         marker=dict(color="#6eb8ea")))
    fig.update_layout(height=300,margin=dict(l=20,r=30,t=10,b=25),
                      paper_bgcolor="#0b1219",plot_bgcolor="#0b1219",
                      xaxis=dict(range=[0,1],title="Model probability for this synthetic scenario",tickformat=".0%",gridcolor="#243947"),
                      yaxis=dict(title="Effort class",gridcolor="#243947"),font=dict(color="#dce8f1"),showlegend=False)
    return fig


def v28_cmis_formula(row):
    parts,raw,final=cmis_breakdown(row)
    formula=" + ".join([f"({v} × {w})" for _,v,w,_ in parts])
    return parts,raw,final,formula


def v28_processing_trace(row, pred, conf, final_cmis, affected, depth):
    tech=len(technical_dependencies(row.id))
    dependents=max(len(dependency_depths(row.id))-len(direct_owner(row.id)),0)
    trace=[
        ("01","INPUT","Selected cryptographic asset",f"{row.id} · {row['name']}"),
        ("02","GRAPH","Dependency traversal",f"{affected} affected component(s) · depth {depth}"),
        ("03","ENGINEERING","Technical dependency extraction",f"{tech} protocol/library relationship(s) · {dependents} downstream dependent(s)"),
        ("04","RISK","CMIS calculation",f"{final_cmis}/100 · {row['Risk']} modeled band"),
        ("05","AI","Random Forest inference",f"{pred} effort · {conf:.1f}% model confidence"),
        ("06","DECISION","Planning hand-off", "Preparation gates + migration sequence + simulation target"),
    ]
    html_rows="".join(f"<div class='v28-trace-row'><div class='v28-trace-num'>{n}</div><div><span>{html.escape(k)}</span><b>{html.escape(a)}</b><small>{html.escape(v)}</small></div></div>" for n,k,a,v in trace)
    return f"<div class='v28-processing-trace'><div class='v28-trace-head'><span>LIVE NEXORA PROCESSING TRACE</span><b>How this result was produced from the selected asset</b></div>{html_rows}</div>"



def local_host_evidence_fast():
    """Collect modular, read-only evidence that maps to NEXORA discovery layers.

    Windows collection is intentionally split into independent probes. A failure in
    certificates must not erase processes, services or network evidence. The collector
    reports each probe independently so the UI can distinguish OBSERVED from unavailable.
    """
    ev={
        "timestamp":datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "hostname":socket.gethostname(),"platform":platform.platform(),
        "os":f"{platform.system()} {platform.release()}","os_version":platform.version(),
        "architecture":platform.machine(),"python":platform.python_version(),
        "python_executable":sys.executable if 'sys' in globals() else "N/A",
        "interfaces":[],"interface_records":[],"interface_addresses":[],
        "listening_ports":[],"listening_records":[],"processes":None,"process_sample":[],
        "services_count":None,"running_services":None,"service_records":[],
        "certificate_count":None,"certificate_records":[],"network_config_records":[],
        "default_gateways":[],"dns_servers":[],"crypto_implementations":[],
        "python_crypto_packages":[],"collector_methods":[],"collection_warnings":[],
        "probe_status":{},"user":os.environ.get("USERNAME") or os.environ.get("USER") or "N/A",
        "system_manufacturer":"N/A","system_model":"N/A","domain":"N/A",
        "evidence_scope":"execution host only","telemetry_status":"PARTIAL",
        "cpu_percent":None,"cpu_model":platform.processor() or "Not reported","cpu_logical":None,
        "cpu_physical":None,"memory":None,"memory_used":None,"memory_total_gb":None,
        "memory_available_gb":None,"disk":None,"disk_total_gb":None,"disk_free_gb":None,
        "disk_records":[],"uptime":None,"boot_time":None,"firewall_records":[],
    }
    def note(msg):
        if msg not in ev["collection_warnings"]: ev["collection_warnings"].append(msg)
    def normalize(value):
        if value is None: return []
        if isinstance(value,list): return value
        return [value]
    def ps_json(label, script, timeout=7):
        try:
            raw=_run_command(["powershell.exe","-NoLogo","-NoProfile","-NonInteractive","-ExecutionPolicy","Bypass","-Command",script],timeout=timeout)
            if not raw:
                ev["probe_status"][label]={"status":"UNAVAILABLE","reason":"No output returned"};return None
            data=json.loads(raw);ev["probe_status"][label]={"status":"OBSERVED"};return data
        except json.JSONDecodeError:
            ev["probe_status"][label]={"status":"UNAVAILABLE","reason":"Malformed JSON"};note(f"{label}: malformed JSON returned by PowerShell.")
        except Exception as e:
            ev["probe_status"][label]={"status":"UNAVAILABLE","reason":type(e).__name__};note(f"{label}: {type(e).__name__}.")
        return None

    try:
        from importlib import metadata as importlib_metadata
        for pkg in ("cryptography","pyOpenSSL","paramiko"):
            try: ev["python_crypto_packages"].append({"Package":pkg,"Version":importlib_metadata.version(pkg)})
            except importlib_metadata.PackageNotFoundError: pass
        ev["probe_status"]["Python crypto packages"]={"status":"OBSERVED","count":len(ev["python_crypto_packages"])}
    except Exception as e:
        ev["probe_status"]["Python crypto packages"]={"status":"UNAVAILABLE","reason":type(e).__name__};note(f"Python package metadata unavailable: {type(e).__name__}.")

    if platform.system().lower()=="windows":
        ev["collector_methods"].append("Windows native modular discovery")
        system=ps_json("Host identity", r'''$x=Get-CimInstance Win32_ComputerSystem -ErrorAction Stop; [pscustomobject]@{Manufacturer=$x.Manufacturer;Model=$x.Model;Domain=$x.Domain;UserName=$x.UserName}|ConvertTo-Json -Compress''',6)
        osinfo=ps_json("OS identity", r'''$x=Get-CimInstance Win32_OperatingSystem -ErrorAction Stop; [pscustomobject]@{Caption=$x.Caption;Version=$x.Version;BuildNumber=$x.BuildNumber;OSArchitecture=$x.OSArchitecture;LastBootUpTime=$x.LastBootUpTime}|ConvertTo-Json -Compress''',6)
        if isinstance(system,list): system=system[0] if system else {}
        if isinstance(osinfo,list): osinfo=osinfo[0] if osinfo else {}
        if system:
            ev["system_manufacturer"]=system.get("Manufacturer") or "N/A";ev["system_model"]=system.get("Model") or "N/A";ev["domain"]=system.get("Domain") or "N/A"
            if system.get("UserName"): ev["user"]=system.get("UserName")
        if osinfo:
            ev["os"]=osinfo.get("Caption") or ev["os"];ev["os_version"]=f"{osinfo.get('Version') or ev['os_version']} build {osinfo.get('BuildNumber') or 'N/A'}";ev["architecture"]=osinfo.get("OSArchitecture") or ev["architecture"]

        processes=ps_json("Process inventory", r'''$rows=@(Get-Process -ErrorAction SilentlyContinue | Sort-Object WorkingSet64 -Descending | Select-Object -First 80 ProcessName,Id,WS,CPU); [pscustomobject]@{Rows=$rows}|ConvertTo-Json -Depth 5 -Compress''',8)
        rows=normalize((processes or {}).get("Rows") if isinstance(processes,dict) else processes)
        ev["process_sample"]= [{"PID":x.get("Id") or "—","Process":x.get("ProcessName") or "Unknown","Status":"running","Memory MB":round(float(x.get("WS") or 0)/1024**2,1),"CPU seconds":round(float(x.get("CPU") or 0),2) if str(x.get("CPU") or "").replace(".","",1).isdigit() else "—"} for x in rows if isinstance(x,dict)]
        ev["processes"]=len(ev["process_sample"]) if processes is not None else None

        services=ps_json("Windows services", r'''$rows=@(Get-Service -ErrorAction SilentlyContinue | Select-Object Name,DisplayName,Status,StartType); [pscustomobject]@{Rows=$rows}|ConvertTo-Json -Depth 5 -Compress''',8)
        rows=normalize((services or {}).get("Rows") if isinstance(services,dict) else services)
        ev["service_records"]=[{"Name":x.get("Name") or "—","Display Name":x.get("DisplayName") or "—","Status":str(x.get("Status") or "—"),"Start Type":str(x.get("StartType") or "—")} for x in rows if isinstance(x,dict)]
        ev["services_count"]=len(ev["service_records"]) if services is not None else None;ev["running_services"]=sum(str(x.get("Status","")).lower()=="running" for x in ev["service_records"]) if services is not None else None

        net=ps_json("Network configuration", r'''$rows=@(Get-NetIPConfiguration -All -ErrorAction SilentlyContinue | ForEach-Object {[pscustomobject]@{Interface=$_.InterfaceAlias;IPv4=(@($_.IPv4Address|ForEach-Object{$_.IPAddress})-join ', ');IPv6=(@($_.IPv6Address|ForEach-Object{$_.IPAddress})-join ', ');Gateway=(@($_.IPv4DefaultGateway|ForEach-Object{$_.NextHop})-join ', ');DNS=(@($_.DNSServer.ServerAddresses)-join ', ')}}); [pscustomobject]@{Rows=$rows}|ConvertTo-Json -Depth 6 -Compress''',8)
        rows=normalize((net or {}).get("Rows") if isinstance(net,dict) else net)
        ev["network_config_records"]=[{"Interface":x.get("Interface") or "—","IPv4":x.get("IPv4") or "—","IPv6":x.get("IPv6") or "—","Gateway":x.get("Gateway") or "—","DNS":x.get("DNS") or "—"} for x in rows if isinstance(x,dict)]
        ev["interfaces"]=[x["Interface"] for x in ev["network_config_records"] if x.get("Interface") not in (None,"—")]
        ev["interface_records"]= [{"Interface":x.get("Interface") or "—","Status":"Observed","IPv4":x.get("IPv4") or "—","IPv6":x.get("IPv6") or "—","Gateway":x.get("Gateway") or "—","DNS":x.get("DNS") or "—"} for x in ev["network_config_records"]]
        ev["interface_addresses"]=[f"{x['Interface']}: {x['IPv4']}" for x in ev["network_config_records"] if x.get("IPv4") not in (None,"—","")]
        ev["default_gateways"]=sorted({g.strip() for x in ev["network_config_records"] for g in str(x.get("Gateway") or "").split(",") if g.strip() and g.strip()!="—"})
        ev["dns_servers"]=sorted({d.strip() for x in ev["network_config_records"] for d in str(x.get("DNS") or "").split(",") if d.strip() and d.strip()!="—"})

        listeners=ps_json("TCP listeners", r'''$rows=@(Get-NetTCPConnection -State Listen -ErrorAction SilentlyContinue | Select-Object LocalAddress,LocalPort,OwningProcess); [pscustomobject]@{Rows=$rows}|ConvertTo-Json -Depth 5 -Compress''',8)
        rows=normalize((listeners or {}).get("Rows") if isinstance(listeners,dict) else listeners);proc_by_id={str(x.get("PID")):x.get("Process") for x in ev["process_sample"]}
        ev["listening_records"]=[{"Port":x.get("LocalPort") or "—","Address":x.get("LocalAddress") or "—","PID":x.get("OwningProcess") or "—","Process":proc_by_id.get(str(x.get("OwningProcess")),"Not correlated")} for x in rows if isinstance(x,dict)]
        ev["listening_ports"]=sorted({int(x["Port"]) for x in ev["listening_records"] if str(x.get("Port")).isdigit()})

        certs=ps_json("Local certificates", r'''$rows=@(Get-ChildItem Cert:\LocalMachine\My -ErrorAction SilentlyContinue | Select-Object Subject,Issuer,Thumbprint,NotBefore,NotAfter,HasPrivateKey,@{N='SignatureAlgorithm';E={try{$_.SignatureAlgorithm.FriendlyName}catch{''}}},@{N='PublicKeyAlgorithm';E={try{$_.PublicKey.Oid.FriendlyName}catch{''}}},@{N='KeySize';E={try{$_.PublicKey.Key.KeySize}catch{''}}},@{N='EnhancedKeyUsage';E={try{($_.EnhancedKeyUsageList|ForEach-Object{$_.FriendlyName})-join '; '}catch{''}}}); [pscustomobject]@{Rows=$rows}|ConvertTo-Json -Depth 6 -Compress''',10)
        rows=normalize((certs or {}).get("Rows") if isinstance(certs,dict) else certs)
        ev["certificate_records"]=[{"Subject":x.get("Subject") or "—","Issuer":x.get("Issuer") or "—","Thumbprint":x.get("Thumbprint") or "—","Valid From":str(x.get("NotBefore") or "—"),"Valid Until":str(x.get("NotAfter") or "—"),"Private Key":"present" if str(x.get("HasPrivateKey")).lower()=="true" else "not present/unknown","Signature Algorithm":str(x.get("SignatureAlgorithm") or "—"),"Public Key Algorithm":str(x.get("PublicKeyAlgorithm") or "—"),"Key Size":str(x.get("KeySize") or "—"),"Enhanced Key Usage":str(x.get("EnhancedKeyUsage") or "—")} for x in rows if isinstance(x,dict)]
        ev["certificate_count"]=len(ev["certificate_records"]) if certs is not None else None

        crypto=ps_json("Crypto implementations", r'''$rows=@(); foreach($n in @('openssl','ssh','ssh-keygen')){try{$c=Get-Command $n -ErrorAction Stop;$path=if($c.Source){$c.Source}else{$c.Path};$ver='Not reported';try{$ver=(Get-Item $path -ErrorAction Stop).VersionInfo.FileVersion}catch{};$rows+=[pscustomobject]@{Implementation=$n;Path=$path;Version=$ver}}catch{}}; [pscustomobject]@{Rows=$rows}|ConvertTo-Json -Depth 5 -Compress''',6)
        rows=normalize((crypto or {}).get("Rows") if isinstance(crypto,dict) else crypto);ev["crypto_implementations"]=[{"Implementation":x.get("Implementation") or "—","Path":x.get("Path") or "—","Version":x.get("Version") or "Not reported"} for x in rows if isinstance(x,dict)]

        resources=ps_json("Host resource context", r'''$os=Get-CimInstance Win32_OperatingSystem -ErrorAction SilentlyContinue;$cpu=Get-CimInstance Win32_Processor -ErrorAction SilentlyContinue|Select-Object -First 1;[pscustomobject]@{MemoryTotalGB=if($os){[math]::Round($os.TotalVisibleMemorySize/1MB,2)}else{$null};MemoryFreeGB=if($os){[math]::Round($os.FreePhysicalMemory/1MB,2)}else{$null};CPUModel=if($cpu){$cpu.Name}else{$null}}|ConvertTo-Json -Compress''',6)
        if resources:
            ev["memory_total_gb"]=resources.get("MemoryTotalGB");ev["memory_available_gb"]=resources.get("MemoryFreeGB");ev["cpu_model"]=resources.get("CPUModel") or ev["cpu_model"]
        core=["Process inventory","Windows services","Network configuration","TCP listeners","Local certificates","Crypto implementations"]
        ok=sum(ev.get("probe_status",{}).get(k,{}).get("status")=="OBSERVED" for k in core)
        ev["telemetry_status"]="COMPLETE" if ok==len(core) else ("PARTIAL" if ok else "FAILED")
    else:
        if psutil is None:
            note("Non-Windows portable collector requires psutil.");ev["telemetry_status"]="FAILED"
        else:
            ev["collector_methods"].append("psutil portable fallback")
            try:
                records=[]
                for proc in psutil.process_iter(["pid","name","status","memory_info"]):
                    try:
                        mi=proc.info.get("memory_info");records.append({"PID":proc.info.get("pid"),"Process":proc.info.get("name") or "Unknown","Status":proc.info.get("status") or "—","Memory MB":round((mi.rss if mi else 0)/1024**2,1)})
                    except Exception: continue
                ev["process_sample"]=records[:80];ev["processes"]=len(records);ev["probe_status"]["Process inventory"]={"status":"OBSERVED"}
            except Exception as e: note(f"Process inventory unavailable: {type(e).__name__}")
            try:
                rows=[]
                for name,entries in psutil.net_if_addrs().items():
                    ipv4=[a.address for a in entries if getattr(a,"family",None)==socket.AF_INET];ipv6=[a.address.split('%')[0] for a in entries if getattr(a,"family",None)==socket.AF_INET6]
                    rows.append({"Interface":name,"Status":"Observed","IPv4":", ".join(ipv4) or "—","IPv6":", ".join(ipv6) or "—","Gateway":"Not collected","DNS":"Not collected"})
                ev["interface_records"]=rows;ev["interfaces"]=[r["Interface"] for r in rows];ev["network_config_records"]=rows;ev["probe_status"]["Network configuration"]={"status":"OBSERVED"}
            except Exception as e: note(f"Interface inventory unavailable: {type(e).__name__}")
            ev["telemetry_status"]="PARTIAL"
    return ev

def local_host_evidence_v28():
    """Broad, read-only local evidence collector with multiple Windows fallbacks.
    It never exports private keys and never changes services, firewall or network state.
    Availability depends on OS permissions and installed management interfaces.
    """
    ev={
        "timestamp":datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "hostname":socket.gethostname(),"platform":platform.platform(),
        "os":f"{platform.system()} {platform.release()}","os_version":platform.version(),
        "architecture":platform.machine(),"python":platform.python_version(),
        "python_executable":sys.executable if 'sys' in globals() else "N/A",
        "working_directory":os.getcwd(),"processor":platform.processor() or "Not reported",
        "cpu_logical":None,"cpu_physical":None,"cpu_percent":None,"cpu_model":platform.processor() or "Not reported",
        "memory":None,"memory_used":None,"memory_total_gb":None,"memory_available_gb":None,
        "disk":None,"disk_total_gb":None,"disk_free_gb":None,
        "interfaces":[],"interface_records":[],"interface_addresses":[],
        "listening_ports":[],"listening_records":[],
        "uptime":None,"boot_time":None,"processes":None,"process_sample":[],
        "services_count":None,"running_services":None,"service_records":[],
        "certificate_count":None,"certificate_records":[],"firewall_records":[],
        "collector_methods":[],"collection_warnings":[],"user":os.environ.get("USERNAME") or os.environ.get("USER") or "N/A",
        "system_manufacturer":"N/A","system_model":"N/A","domain":"N/A"
    }
    def note(msg):
        if msg not in ev["collection_warnings"]: ev["collection_warnings"].append(msg)
    # psutil first when available
    if psutil is not None:
        ev["collector_methods"].append("psutil")
        try: ev["processes"]=len(psutil.pids())
        except Exception as e: note(f"Process count unavailable: {type(e).__name__}")
        try: ev["cpu_logical"]=psutil.cpu_count(logical=True); ev["cpu_physical"]=psutil.cpu_count(logical=False)
        except Exception as e: note(f"CPU topology unavailable: {type(e).__name__}")
        try: ev["cpu_percent"]=round(float(psutil.cpu_percent(interval=.35)),1)
        except Exception as e: note(f"CPU utilization unavailable: {type(e).__name__}")
        try:
            mem=psutil.virtual_memory(); ev["memory_total_gb"]=round(mem.total/1024**3,1); ev["memory_available_gb"]=round(mem.available/1024**3,1); ev["memory_used"]=f"{mem.percent:.0f}% used"; ev["memory"]=f"{mem.total/1024**3:.1f} GB"
        except Exception as e: note(f"Memory telemetry unavailable: {type(e).__name__}")
        try:
            du=psutil.disk_usage(Path.home().anchor or "/"); ev["disk_total_gb"]=round(du.total/1024**3,1); ev["disk_free_gb"]=round(du.free/1024**3,1); ev["disk"]=f"{du.percent:.0f}% used"
        except Exception as e: note(f"Disk telemetry unavailable: {type(e).__name__}")
        try:
            bt=psutil.boot_time(); ev["boot_time"]=datetime.fromtimestamp(bt).strftime("%Y-%m-%d %H:%M:%S"); ev["uptime"]=str(timedelta(seconds=max(0,int(time.time()-bt))))
        except Exception as e: note(f"Boot/uptime unavailable: {type(e).__name__}")
        try:
            addrs=psutil.net_if_addrs(); stats=psutil.net_if_stats(); rows=[]
            for name,entries in addrs.items():
                ipv4=[];ipv6=[];mac="—"
                for a in entries:
                    fam=getattr(a,"family",None)
                    if fam==socket.AF_INET: ipv4.append(a.address)
                    elif fam==socket.AF_INET6: ipv6.append(a.address.split('%')[0])
                    elif str(fam).endswith("AF_LINK") or str(fam).endswith("AF_PACKET"): mac=a.address or "—"
                stt=stats.get(name); rows.append({"Interface":name,"Status":"UP" if (stt and stt.isup) else "DOWN/UNKNOWN","Speed":f"{stt.speed} Mbps" if (stt and stt.speed and stt.speed>0) else "N/A","IPv4":", ".join(ipv4) or "—","IPv6":", ".join(ipv6) or "—","MAC":mac,"Gateway":"—","DNS":"OS-resolved"})
            ev["interface_records"]=rows; ev["interfaces"]=[r["Interface"] for r in rows]
            for r in rows:
                if r["IPv4"]!="—": ev["interface_addresses"].append(f"{r['Interface']}: {r['IPv4']}")
        except Exception as e: note(f"Interface telemetry unavailable: {type(e).__name__}")
        try:
            records=[]
            for proc in psutil.process_iter(["pid","name","status","memory_info","username","create_time"]):
                try:
                    mi=proc.info.get("memory_info"); ct=proc.info.get("create_time")
                    records.append({"PID":proc.info.get("pid"),"Process":proc.info.get("name") or "Unknown","Status":proc.info.get("status") or "—","Memory MB":round((mi.rss if mi else 0)/1024**2,1),"User":proc.info.get("username") or "—","Started":datetime.fromtimestamp(ct).strftime("%H:%M:%S") if ct else "—"})
                except Exception: continue
            ev["process_sample"]=sorted(records,key=lambda x:float(x.get("Memory MB") or 0),reverse=True)[:30]
        except Exception as e: note(f"Process inventory unavailable: {type(e).__name__}")
        try:
            conns=psutil.net_connections(kind="inet"); lr=[]
            for c in conns:
                if c.status!=psutil.CONN_LISTEN or not c.laddr: continue
                pid=getattr(c,"pid",None); pn="Unknown"
                if pid:
                    try: pn=psutil.Process(pid).name()
                    except Exception: pass
                lr.append({"Port":c.laddr.port,"Address":c.laddr.ip,"PID":pid or "—","Process":pn})
            ev["listening_records"]=sorted(lr,key=lambda x:(int(x["Port"]),str(x["Process"])))[:100];ev["listening_ports"]=sorted({x["Port"] for x in ev["listening_records"]})
        except Exception as e: note(f"Socket inventory unavailable: {type(e).__name__}")
    # Windows-native enrichment is always attempted, even when psutil is installed.
    if platform.system().lower()=="windows":
        ev["collector_methods"].append("Windows PowerShell / native commands")
        def psjson(cmd, label):
            try:
                raw=_run_command(["powershell","-NoProfile","-Command",cmd],timeout=12)
                if not raw: raise RuntimeError("empty output")
                return json.loads(raw)
            except Exception as e:
                note(f"{label} unavailable: {type(e).__name__}"); return None
        cs=psjson("Get-CimInstance Win32_ComputerSystem | Select Manufacturer,Model,Domain,NumberOfLogicalProcessors,NumberOfProcessors | ConvertTo-Json -Compress","system profile")
        if isinstance(cs,dict):
            ev["system_manufacturer"]=cs.get("Manufacturer") or "N/A";ev["system_model"]=cs.get("Model") or "N/A";ev["domain"]=cs.get("Domain") or "N/A"
            ev["cpu_logical"]=ev["cpu_logical"] or cs.get("NumberOfLogicalProcessors");ev["cpu_physical"]=ev["cpu_physical"] or cs.get("NumberOfProcessors")
        osinfo=psjson("Get-CimInstance Win32_OperatingSystem | Select Caption,Version,BuildNumber,LastBootUpTime,TotalVisibleMemorySize,FreePhysicalMemory,OSArchitecture | ConvertTo-Json -Compress","OS profile")
        if isinstance(osinfo,dict):
            ev["os"]=osinfo.get("Caption") or ev["os"];ev["os_version"]=str(osinfo.get("Version") or ev["os_version"])+f" build {osinfo.get('BuildNumber') or 'N/A'}";ev["architecture"]=osinfo.get("OSArchitecture") or ev["architecture"]
            try:
                total=float(osinfo.get("TotalVisibleMemorySize") or 0)/1024**2; free=float(osinfo.get("FreePhysicalMemory") or 0)/1024**2
                if total: ev["memory_total_gb"]=round(total,1);ev["memory_available_gb"]=round(free,1);ev["memory_used"]=f"{((total-free)/total*100):.0f}% used";ev["memory"]=f"{total:.1f} GB"
            except Exception: pass
            rawbt=osinfo.get("LastBootUpTime")
            if rawbt and not ev.get("boot_time"):
                try:
                    stime=str(rawbt).split("+")[0].split(".")[0]; dt=datetime.strptime(stime,"%Y%m%d%H%M%S");ev["boot_time"]=dt.strftime("%Y-%m-%d %H:%M:%S");ev["uptime"]=str(datetime.now()-dt)
                except Exception: pass
        cpuinfo=psjson("Get-CimInstance Win32_Processor | Select Name,NumberOfCores,NumberOfLogicalProcessors,LoadPercentage,MaxClockSpeed | ConvertTo-Json -Compress","CPU profile")
        if isinstance(cpuinfo,dict): cpuinfo=[cpuinfo]
        if cpuinfo:
            ev["cpu_model"]=cpuinfo[0].get("Name") or ev["cpu_model"];ev["cpu_physical"]=ev["cpu_physical"] or sum(int(x.get("NumberOfCores") or 0) for x in cpuinfo);ev["cpu_logical"]=ev["cpu_logical"] or sum(int(x.get("NumberOfLogicalProcessors") or 0) for x in cpuinfo);loads=[x.get("LoadPercentage") for x in cpuinfo if x.get("LoadPercentage") is not None];ev["cpu_percent"]=round(sum(loads)/len(loads),1) if loads else ev["cpu_percent"]
        disks=psjson("Get-CimInstance Win32_LogicalDisk -Filter \"DriveType=3\" | Select DeviceID,VolumeName,Size,FreeSpace | ConvertTo-Json -Compress","disk inventory")
        if isinstance(disks,dict): disks=[disks]
        ev["disk_records"]=[]
        if disks:
            total=sum(float(x.get("Size") or 0) for x in disks);free=sum(float(x.get("FreeSpace") or 0) for x in disks);ev["disk_total_gb"]=round(total/1024**3,1);ev["disk_free_gb"]=round(free/1024**3,1);ev["disk"]=f"{((total-free)/total*100):.0f}% used" if total else "N/A"
            for x in disks: ev["disk_records"].append({"Drive":x.get("DeviceID") or "—","Volume":x.get("VolumeName") or "—","Size GB":round(float(x.get("Size") or 0)/1024**3,1),"Free GB":round(float(x.get("FreeSpace") or 0)/1024**3,1)})
        services=psjson("Get-Service | Select Name,DisplayName,Status,StartType | ConvertTo-Json -Compress","service inventory")
        if isinstance(services,dict): services=[services]
        if services:
            ev["service_records"]=[{"Name":x.get("Name") or "—","Display Name":x.get("DisplayName") or "—","Status":str(x.get("Status") or "—"),"Start Type":str(x.get("StartType") or "—")} for x in services];ev["services_count"]=len(ev["service_records"]);ev["running_services"]=sum(str(x["Status"]).lower()=="running" for x in ev["service_records"])
        adapters=psjson("Get-NetAdapter | Select Name,InterfaceDescription,Status,MacAddress,LinkSpeed,ifIndex | ConvertTo-Json -Compress","network adapter inventory")
        if isinstance(adapters,dict): adapters=[adapters]
        ips=psjson("Get-NetIPConfiguration | Select InterfaceAlias,IPv4Address,IPv6Address,IPv4DefaultGateway,DNSServer | ConvertTo-Json -Compress","IP configuration")
        if isinstance(ips,dict): ips=[ips]
        ipmap={}
        for x in ips or []:
            alias=x.get("InterfaceAlias") or "—"
            def val(v):
                if isinstance(v,list): return ", ".join(str((z.get("IPAddress") if isinstance(z,dict) else z) or "—") for z in v)
                return str(v.get("NextHop") if isinstance(v,dict) else (v or "—"))
            ipmap[alias]={"IPv4":val(x.get("IPv4Address")),"IPv6":val(x.get("IPv6Address")),"Gateway":val(x.get("IPv4DefaultGateway")),"DNS":val(x.get("DNSServer"))}
        if adapters:
            rows=[]
            for x in adapters:
                name=x.get("Name") or "—"; extra=ipmap.get(name,{})
                rows.append({"Interface":name,"Description":x.get("InterfaceDescription") or "—","Status":x.get("Status") or "—","Speed":x.get("LinkSpeed") or "—","MAC":x.get("MacAddress") or "—","IPv4":extra.get("IPv4","—"),"IPv6":extra.get("IPv6","—"),"Gateway":extra.get("Gateway","—"),"DNS":extra.get("DNS","—")})
            ev["interface_records"]=rows;ev["interfaces"]=[r["Interface"] for r in rows];ev["interface_addresses"]=[f"{r['Interface']}: {r['IPv4']}" for r in rows if r["IPv4"]!="—"]
        listeners=psjson("Get-NetTCPConnection -State Listen | Select LocalAddress,LocalPort,OwningProcess | Sort LocalPort | ConvertTo-Json -Compress","TCP listener inventory")
        if isinstance(listeners,dict): listeners=[listeners]
        if listeners:
            # Process-name lookup is deliberately separate so a permission failure does not erase socket evidence.
            lr=[]
            for x in listeners[:100]:
                pid=x.get("OwningProcess") or "—"; pname="Unknown"
                try: pname=subprocess.check_output(["powershell","-NoProfile","-Command",f"(Get-Process -Id {int(pid)}).ProcessName"],text=True,timeout=3).strip() or "Unknown"
                except Exception: pass
                lr.append({"Port":x.get("LocalPort") or "—","Address":x.get("LocalAddress") or "—","PID":pid,"Process":pname})
            ev["listening_records"]=lr;ev["listening_ports"]=[x["Port"] for x in lr]
        certs=psjson("Get-ChildItem Cert:\\LocalMachine\\My | Select Subject,Thumbprint,NotBefore,NotAfter,HasPrivateKey,@{N='SignatureAlgorithm';E={$_.SignatureAlgorithm.FriendlyName}} | ConvertTo-Json -Compress","local certificate store")
        if isinstance(certs,dict): certs=[certs]
        if certs:
            ev["certificate_records"]=[{"Subject":x.get("Subject") or "—","Thumbprint":x.get("Thumbprint") or "—","Valid From":str(x.get("NotBefore") or "—"),"Valid Until":str(x.get("NotAfter") or "—"),"Private Key":str(x.get("HasPrivateKey") or "False"),"Signature Algorithm":str(x.get("SignatureAlgorithm") or "—")} for x in certs];ev["certificate_count"]=len(ev["certificate_records"])
        fw=psjson("Get-NetFirewallProfile | Select Name,Enabled,DefaultInboundAction,DefaultOutboundAction | ConvertTo-Json -Compress","firewall profile inventory")
        if isinstance(fw,dict): fw=[fw]
        if fw: ev["firewall_records"]=[{"Profile":x.get("Name") or "—","Enabled":str(x.get("Enabled") or "False"),"Inbound":str(x.get("DefaultInboundAction") or "—"),"Outbound":str(x.get("DefaultOutboundAction") or "—")} for x in fw]
        # tasklist fallback if process sample/count is still empty
        if not ev.get("process_sample"):
            try:
                raw=_run_command(["tasklist","/fo","csv","/nh"],timeout=8);import csv,io;rows=[]
                for r in csv.reader(io.StringIO(raw)):
                    if len(r)>=5:
                        mem=re.sub(r"[^0-9]","",r[4]);rows.append({"PID":int(r[1]) if r[1].isdigit() else r[1],"Process":r[0],"Status":"RUNNING","Memory MB":round(int(mem)/1024,1) if mem else 0,"User":"OS tasklist","Started":"—"})
                ev["process_sample"]=sorted(rows,key=lambda x:float(x.get("Memory MB") or 0),reverse=True)[:30];ev["processes"]=len(rows);ev["collector_methods"].append("tasklist fallback")
            except Exception as e: note(f"tasklist fallback unavailable: {type(e).__name__}")
        if not ev.get("listening_records"):
            try:
                raw=_run_command(["netstat","-ano","-p","TCP"],timeout=8);lr=[]
                for line in raw.splitlines():
                    parts=re.split(r"\s+",line.strip())
                    if len(parts)>=5 and parts[0].upper()=="TCP" and parts[3].upper()=="LISTENING":
                        local=parts[1];pid=parts[4];lr.append({"Port":int(local.rsplit(":",1)[-1]),"Address":local.rsplit(":",1)[0],"PID":int(pid) if pid.isdigit() else pid,"Process":"Unknown"})
                ev["listening_records"]=lr[:100];ev["listening_ports"]=[x["Port"] for x in lr[:100]];ev["collector_methods"].append("netstat fallback")
            except Exception as e: note(f"netstat fallback unavailable: {type(e).__name__}")
    ev["collector"]=" + ".join(dict.fromkeys(ev["collector_methods"])) if ev["collector_methods"] else "Python standard-library collector"
    return ev


# ============================================================
# CASE OVERVIEW VISUAL ENGINE
# ============================================================


def case_overview_domain_model():
    """Compact domain abstraction for CASE only. It is intentionally not the ACDKG."""
    p=SCENARIOS[st.session_state.selected_environment]
    domains=[
        ("EDGE & ACCESS","web","vpn","Web access, remote access and perimeter entry"),
        ("IDENTITY & PKI","auth",None,"Authentication, certificates and trust"),
        ("APPLICATION & API","app","api","Business logic, APIs and service calls"),
        ("DATA SERVICES","db",None,"Databases and transaction-facing services"),
        ("ADMINISTRATION","admin","ssh","Administrative endpoints and SSH"),
        ("LEGACY / SPECIAL","legacy",None,"Older or case-specific services"),
    ]
    assets=df.copy()
    rows=[]
    for label,k1,k2,desc in domains:
        keys=[k for k in (k1,k2) if k]
        names=[p["roles"][k] for k in keys if k in p["roles"]]
        extra=[]
        for _,r in COMPONENTS.iterrows():
            nm=str(r.iloc[1])
            if nm not in p["roles"].values():
                low=nm.lower()
                if label=="LEGACY / SPECIAL": extra.append(nm)
        count=sum(1 for k in keys if k in p["roles"]) + (len(extra) if label=="LEGACY / SPECIAL" else 0)
        crypto=int(assets.owner.isin(names).sum())
        rows.append((label,count,crypto,desc))
    return rows


def case_crypto_surface_figure():
    """CASE-level crypto distribution: infrastructure domain -> role -> algorithm.
    This is a surface distribution view, not the ACDKG dependency graph.
    """
    if df.empty: return go.Figure()
    p=SCENARIOS[st.session_state.selected_environment]
    role_to_domain={
        "web":"EDGE & ACCESS","vpn":"EDGE & ACCESS","auth":"IDENTITY & PKI",
        "app":"APPLICATION & API","api":"APPLICATION & API","db":"DATA SERVICES",
        "admin":"ADMINISTRATION","ssh":"ADMINISTRATION","legacy":"LEGACY / SPECIAL"
    }
    owner_to_domain={v:role_to_domain.get(k,"LEGACY / SPECIAL") for k,v in p["roles"].items()}
    groups=[];roles=[];algos=[]
    for _,r in df.iterrows():
        groups.append(owner_to_domain.get(str(r.get("owner")),"CONTEXT NOT MAPPED"))
        roles.append(str(r.get("crypto_role","Unknown")))
        algos.append(str(r.get("algorithm","Unknown")))
    labels=[]
    for x in groups+roles+algos:
        if x not in labels: labels.append(x)
    idx={x:i for i,x in enumerate(labels)}
    source=[];target=[];value=[]
    from collections import Counter
    c1=Counter(zip(groups,roles));c2=Counter(zip(roles,algos))
    for (a,b),v in c1.items(): source.append(idx[a]);target.append(idx[b]);value.append(v)
    for (a,b),v in c2.items(): source.append(idx[a]);target.append(idx[b]);value.append(v)
    domain_colors={"EDGE & ACCESS":"#4fb3ff","IDENTITY & PKI":"#8d7cff","APPLICATION & API":"#55d6be","DATA SERVICES":"#ffb454","ADMINISTRATION":"#c58cff","LEGACY / SPECIAL":"#7d92a6","CONTEXT NOT MAPPED":"#ef6b73"}
    role_colors={"Digital Signature":"#2d8fe3","Key Establishment":"#df8f9d"}
    algo_colors={"RSA-2048":"#e65a5a","RSA-3072":"#62c78a","ECC-P256":"#31a8a0"}
    node_colors=[domain_colors.get(x,role_colors.get(x,algo_colors.get(x,"#7195ad"))) for x in labels]
    fig=go.Figure(go.Sankey(
        arrangement="snap",
        node=dict(label=labels,pad=22,thickness=22,line=dict(color="#294454",width=1),color=node_colors,
                  hovertemplate="<b>%{label}</b><br>%{value} modeled asset(s)<extra></extra>"),
        link=dict(source=source,target=target,value=value,color="rgba(116,166,198,.22)",
                  hovertemplate="<b>%{source.label}</b> → <b>%{target.label}</b><br>%{value} modeled asset(s)<extra></extra>")
    ))
    fig.update_layout(height=400,margin=dict(l=8,r=8,t=8,b=8),paper_bgcolor="#091219",
                      font=dict(color="#dbe7ee",size=11),hoverlabel=dict(bgcolor="#0d1b25",font_color="#eaf4fb"))
    return fig


def case_comparison_figure(metric="Crypto assets"):
    records=[]
    for name in SCENARIOS:
        tdf,tg,tcomp=build_scenario_data(name)
        if metric=="Crypto assets": val=len(tdf)
        elif metric=="Infrastructure components": val=len(tcomp)
        elif metric=="ACDKG relationships": val=tg.number_of_edges()
        elif metric=="Quantum-vulnerable assets": val=sum(str(r["algorithm"]) in ALGORITHM_VULNERABILITY for _,r in tdf.iterrows())
        elif metric=="Average CMIS":
            vals=[]
            for _,r in tdf.iterrows():
                vuln=ALGORITHM_VULNERABILITY.get(r["algorithm"],2)
                # Use the same project CMIS formula as the live case, computed on the scenario graph.
                owners=[s for s,t,d in tg.edges(data=True) if t==r.id and d.get("relation") in {"uses_crypto_asset","protected_by"}]
                depths={};q=[]
                for owner in owners: depths[owner]=0;q.append(owner)
                while q:
                    cur=q.pop(0)
                    for pred in tg.predecessors(cur):
                        if tg.edges[pred,cur].get("relation")!="depends_on": continue
                        nd=depths[cur]+1
                        if pred not in depths or nd<depths[pred]: depths[pred]=nd;q.append(pred)
                dependency_factor=min(max(len(depths)-1,0),5)
                vals.append(min(round(vuln*8+r["criticality"]*6+r["exposure"]*5+r["complexity"]*4+dependency_factor*3),100))
            val=round(float(np.mean(vals)),1) if vals else 0
        else: val=0
        records.append({"Case":name,"Value":val})
    active=st.session_state.selected_environment
    colors=["#63b6e8" if r["Case"]==active else "#244355" for r in records]
    widths=[1.5 if r["Case"]==active else .5 for r in records]
    fig=go.Figure(go.Bar(x=[r["Case"] for r in records],y=[r["Value"] for r in records],text=[r["Value"] for r in records],textposition="auto",marker=dict(color=colors,line=dict(color="#78c9f2",width=widths))))
    fig.update_layout(height=300,margin=dict(l=8,r=8,t=12,b=55),paper_bgcolor="#091219",plot_bgcolor="#091219",font=dict(color="#dbe7ee",size=10),xaxis=dict(gridcolor="#1d3442",tickangle=0),yaxis=dict(gridcolor="#1d3442",title=metric),hoverlabel=dict(bgcolor="#0d1b25",font_color="#eaf4fb"))
    return fig


def case_change_preview(asset_id,target):
    if asset_id not in df.id.tolist(): return None
    row=df.loc[df.id==asset_id].iloc[0]
    depths=dependency_depths(asset_id); affected=impacted_components(asset_id); tech=technical_dependencies(asset_id)
    p=SCENARIOS[st.session_state.selected_environment]
    role_to_domain={
        "web":"EDGE & ACCESS","vpn":"EDGE & ACCESS","auth":"IDENTITY & PKI",
        "app":"APPLICATION & API","api":"APPLICATION & API","db":"DATA SERVICES",
        "admin":"ADMINISTRATION","ssh":"ADMINISTRATION","legacy":"LEGACY / SPECIAL"
    }
    owner_key=next((k for k,v in p["roles"].items() if v==str(row.owner)),None)
    domains=[]
    if owner_key and role_to_domain.get(owner_key): domains.append(role_to_domain[owner_key])
    for comp in affected:
        key=next((k for k,v in p["roles"].items() if v==comp),None)
        d=role_to_domain.get(key)
        if d and d not in domains: domains.append(d)
    return row,depths,affected,tech,domains

# ============================================================
# V19 ACTIVE INVESTIGATION WORKSPACE
# ============================================================
def v19_focus_asset(row, label="FOCUS ASSET"):
    affected=len(impacted_components(row.id));depth=max(dependency_depths(row.id).values(),default=0)
    st.markdown(f"""<div class='v19-focus'><div class='v19-focus-main'><span>{label}</span><b>{html.escape(str(row.id))} · {html.escape(str(row['name']))}</b></div><div class='v19-focus-stat'><span>CURRENT</span><b>{html.escape(str(row.algorithm))}</b></div><div class='v19-focus-stat'><span>ROLE</span><b>{html.escape(str(row.crypto_role))}</b></div><div class='v19-focus-stat'><span>IMPACT</span><b>{affected} components</b></div><div class='v19-focus-stat'><span>DEPTH</span><b>{depth}</b></div><div class='v19-focus-stat'><span>PQC</span><b>{html.escape(str(row['Suggested PQC']))}</b></div></div>""",unsafe_allow_html=True)

def v19_finding(title,text):
    st.markdown(f"<div class='v19-finding'><span>{html.escape(title)}</span><h2>{text}</h2></div>",unsafe_allow_html=True)

def v19_asset_selector(key,label):
    default=st.session_state.trace_asset if st.session_state.trace_asset in df.id.tolist() else df.iloc[0].id
    selected=st.selectbox(label,df.id.tolist(),index=df.id.tolist().index(default),format_func=asset_label,key=key)
    st.session_state.trace_asset=selected
    return selected

def v19_legend():
    st.markdown("<div class='v19-legend'><span><b>×</b> Crypto asset — migration object</span><span><b>★</b> Library — implementation layer</span><span><b>■</b> Service — owner / consumer</span><span><b>◆</b> Application — downstream software</span><span><b>●</b> Network / component — surrounding context</span></div>",unsafe_allow_html=True)

def v19_path(paths,limit=4):
    for path in paths[:limit]:
        nodes=[]
        for i,item in enumerate(path):
            cls='v19-path-node focus' if str(item).startswith('A') else 'v19-path-node'
            nodes.append(f"<span class='{cls}'>{html.escape(str(item))}</span>")
            if i<len(path)-1:nodes.append("<span class='v19-path-arrow'>→</span>")
        st.markdown("<div class='v19-path-line'>"+"".join(nodes)+"</div>",unsafe_allow_html=True)

def v21_selectable_dataframe(data, key, selected_label_col, selected_state_key, height=300):
    """Render a selectable dataframe when supported by Streamlit; safely fall back to a normal table."""
    event = None
    try:
        event = st.dataframe(data, width="stretch", height=height, hide_index=True, key=key,
                             on_select="rerun", selection_mode="single-row")
    except TypeError:
        st.dataframe(data, width="stretch", height=height, hide_index=True)
        return None
    try:
        rows = list(event.selection.rows)
    except Exception:
        rows = []
    if rows:
        value = data.iloc[rows[0]][selected_label_col]
        st.session_state[selected_state_key] = value
        return value
    return st.session_state.get(selected_state_key)


def v21_inventory_signal(row):
    affected=len(impacted_components(row.id)); depth=max(dependency_depths(row.id).values(),default=0)
    if str(row["Risk"]) in {"CRITICAL","HIGH"} and affected>=3:
        return "TRACE FIRST"
    if affected>=2 or depth>=2:
        return "TRACE"
    return "MONITOR"

# ============================================================
# TRACE / ACDKG — evidence helpers
# ============================================================
def trace_relation_label(rel):
    return {
        "protected_by":"PROTECTED BY",
        "depends_on":"DEPENDS ON",
        "uses_protocol":"USES PROTOCOL",
        "uses_library":"USES LIBRARY",
        "uses_service":"USES SERVICE",
        "communicates_with":"COMMUNICATES WITH",
        "uses_algorithm":"USES ALGORITHM",
    }.get(str(rel), str(rel).replace("_", " ").upper())


def trace_path_map(asset_id):
    """Return the shortest modeled dependency path for every impacted component."""
    paths = asset_paths(asset_id)
    best = {}
    for path in paths:
        if not path:
            continue
        component = path[0]
        if component not in best or len(path) < len(best[component]):
            best[component] = path
    return best


def trace_evidence_rows(asset_id):
    depths = dependency_depths(asset_id)
    owners = set(direct_owner(asset_id))
    path_map = trace_path_map(asset_id)
    rows = []
    for component, depth in sorted(depths.items(), key=lambda x: (x[1], str(x[0]))):
        path = path_map.get(component, [component, asset_id])
        relations = []
        for a, b in zip(path, path[1:]):
            relations.append(G.edges[a, b].get("relation", "unknown"))
        rows.append({
            "Component": component,
            "Layer": "DIRECT OWNER" if component in owners else "TRANSITIVE DEPENDENT",
            "Depth": int(depth),
            "Path": " → ".join(path),
            "Relationships": " → ".join(trace_relation_label(r) for r in relations),
            "Type": str(G.nodes[component].get("node_type", "Component")),
        })
    return pd.DataFrame(rows)


def trace_graph_figure(asset_id):
    """Dependency-first ACDKG view: impact layers are separated from technical context."""
    depths = dependency_depths(asset_id)
    owners = set(direct_owner(asset_id))
    path_map = trace_path_map(asset_id)
    affected = set(depths)
    technical = technical_dependencies(asset_id)

    # Dependency edges are the actual blast-radius calculation. Technical edges are
    # included as context but are intentionally not counted as impact depth.
    dep_nodes = affected | {asset_id}
    dep_edges = []
    path_edges = set()
    for path in path_map.values():
        for a, b in zip(path, path[1:]):
            path_edges.add((a, b))
    for a, b, data in G.edges(data=True):
        if a in dep_nodes and b in dep_nodes and data.get("relation") in {"depends_on", "protected_by"}:
            dep_edges.append((a, b, data.get("relation")))

    max_depth = max(depths.values(), default=0)
    pos = {}
    # Asset is the right-side anchor. Depth 0 is its direct owner; larger depths
    # extend leftward so the visual reads as an outward migration blast radius.
    pos[asset_id] = (1.00, 0.50)
    lane_nodes = {}
    for d in range(max_depth + 1):
        ns = sorted([n for n, dd in depths.items() if dd == d])
        lane_nodes[d] = ns
        x = 0.82 - (d * 0.22)
        if len(ns) == 1:
            ys = [0.50]
        else:
            ys = np.linspace(0.76, 0.24, len(ns)).tolist()
        for n, y in zip(ns, ys):
            pos[n] = (max(0.06, x), float(y))

    # Technical context sits below the dependency chain.
    tech_nodes = []
    for target, rel in technical:
        if target not in tech_nodes:
            tech_nodes.append(target)
    row = df.loc[df.id == asset_id].iloc[0]
    algorithm = str(row.algorithm)
    if algorithm in G.nodes:
        tech_nodes.append(algorithm)
    tech_nodes = list(dict.fromkeys(tech_nodes))
    if tech_nodes:
        xs = np.linspace(0.20, 0.85, len(tech_nodes)).tolist() if len(tech_nodes) > 1 else [0.52]
        for n, x in zip(tech_nodes, xs):
            pos[n] = (float(x), 0.06)

    fig = go.Figure()
    relation_styles = {
        "depends_on": ("#5f8fb0", 2.8),
        "protected_by": ("#70c8f2", 3.4),
        "uses_protocol": ("#8c7ac8", 1.8),
        "uses_library": ("#c59b5e", 1.8),
        "uses_service": ("#65b88e", 1.8),
        "uses_algorithm": ("#a987ff", 1.8),
    }

    # Dependency edges: highlight edges that participate in a displayed shortest path.
    for rel in ["depends_on", "protected_by"]:
        xs, ys = [], []
        for a, b, r in dep_edges:
            if r != rel:
                continue
            if a not in pos or b not in pos:
                continue
            x0, y0 = pos[a]; x1, y1 = pos[b]
            xs += [x0, x1, None]; ys += [y0, y1, None]
        if xs:
            color, width = relation_styles[rel]
            fig.add_trace(go.Scatter(x=xs, y=ys, mode="lines", line=dict(color=color, width=width),
                                     name=trace_relation_label(rel), hoverinfo="skip"))

    # Technical links are shown separately and use dashed lines.
    for target, rel in technical:
        owner_list = direct_owner(asset_id)
        for owner in owner_list:
            if owner not in pos or target not in pos:
                continue
            x0, y0 = pos[owner]; x1, y1 = pos[target]
            fig.add_trace(go.Scatter(x=[x0, x1], y=[y0, y1], mode="lines",
                                     line=dict(color=relation_styles.get(rel, ("#7c8ea4", 1.6))[0], width=1.7, dash="dash"),
                                     name=trace_relation_label(rel), hoverinfo="skip", showlegend=True))
    if algorithm in pos and owners:
        for owner in owners:
            if owner in pos:
                x0, y0 = pos[asset_id]; x1, y1 = pos[algorithm]
                # Keep algorithm connected to the asset as cryptographic context.
        fig.add_trace(go.Scatter(x=[pos[asset_id][0], pos[algorithm][0]], y=[pos[asset_id][1], pos[algorithm][1]],
                                 mode="lines", line=dict(color="#a987ff", width=1.7, dash="dash"),
                                 name="USES ALGORITHM", hoverinfo="skip"))

    node_groups = {}
    for n in pos:
        typ = G.nodes[n].get("node_type", "Crypto Asset" if n == asset_id else "Component")
        node_groups.setdefault(typ, []).append(n)
    colors = {
        "Crypto Asset":"#71c7f4", "Crypto Algorithm":"#a987ff", "Library":"#d6ad69",
        "Protocol":"#9a85cf", "Service":"#63a9d9", "Application":"#d18bb4",
        "Network":"#7c8ea4", "Network Device":"#7c8ea4", "Endpoint":"#9aa8b6",
        "Security Service":"#65bd91", "Component":"#6f8297"
    }
    symbols = {"Crypto Asset":"x", "Crypto Algorithm":"star", "Library":"diamond",
               "Protocol":"hexagon", "Service":"square", "Application":"diamond",
               "Network Device":"hexagon", "Endpoint":"triangle-up", "Security Service":"cross"}

    for typ, nodes in node_groups.items():
        texts=[]; hovers=[]; sizes=[]; xs=[]; ys=[]
        for n in nodes:
            x, y = pos[n]; xs.append(x); ys.append(y); texts.append(str(n))
            if n == asset_id:
                layer = "SELECTED CRYPTO ASSET"
                depth_text = "TARGET"
            elif n in depths:
                layer = "DIRECT OWNER" if n in owners else "TRANSITIVE DEPENDENT"
                depth_text = f"DEPTH {depths[n]}"
            else:
                layer = "TECHNICAL CONTEXT"
                depth_text = "NOT IN BLAST-RADIUS COUNT"
            hovers.append(f"{html.escape(str(n))}<br>Type: {html.escape(str(typ))}<br>{html.escape(layer)}<br>{html.escape(depth_text)}")
            sizes.append(34 if n == asset_id else (23 if n in owners else 18))
        fig.add_trace(go.Scatter(x=xs, y=ys, mode="markers+text", text=texts, textposition="top center",
                                 hovertext=hovers, hoverinfo="text", name=typ,
                                 marker=dict(size=sizes, symbol=symbols.get(typ, "circle"),
                                             color=colors.get(typ, "#7c8ea4"), line=dict(width=1.5, color="#0b1118")),
                                 textfont=dict(size=12,color="#dce8f1")))

    # Lane labels make the dependency semantics explicit.
    annotations=[
        dict(x=0.98,y=0.91,text="CRYPTO ASSET",showarrow=False,font=dict(size=11,color="#70b9ee")),
        dict(x=0.06,y=0.91,text="OUTER DEPENDENCY",showarrow=False,font=dict(size=11,color="#7f9db1")),
        dict(x=0.51,y=0.91,text="IMPACT LAYERS",showarrow=False,font=dict(size=11,color="#7f9db1")),
        dict(x=0.52,y=0.005,text="TECHNICAL CONTEXT · protocol / library / algorithm edges are not counted as dependency depth",showarrow=False,font=dict(size=10,color="#718b9d")),
    ]
    for d in range(max_depth + 1):
        x = max(0.06, 0.82 - d * 0.22)
        annotations.append(dict(x=x,y=0.84,text=f"DEPTH {d}" + (" · DIRECT OWNER" if d==0 else " · TRANSITIVE"),
                                showarrow=False,font=dict(size=10,color="#5f8da8")))

    fig.update_layout(height=560, margin=dict(l=18,r=18,t=24,b=22), paper_bgcolor="#0b1219", plot_bgcolor="#0b1219",
                      font=dict(color="#dce8f1", size=10), xaxis=dict(range=[0,1.05],visible=False),
                      yaxis=dict(range=[0,1],visible=False), showlegend=True,
                      legend=dict(orientation="h",yanchor="bottom",y=1.01,xanchor="left",x=0,
                                  bgcolor="rgba(0,0,0,0)",font=dict(size=10,color="#aebdcb")),
                      annotations=annotations)
    return fig


def trace_summary_card(label, value, detail, cls=""):
    return f"<div class='v35-trace-kpi {cls}'><span>{html.escape(label)}</span><b>{html.escape(str(value))}</b><small>{html.escape(detail)}</small></div>"


# ============================================================
# 01 CASE — CASE COMMAND BRIEF
# ============================================================
# ============================================================
# SIMULATION THEATRE HELPERS — deterministic, evidence-driven
# ============================================================
def simulation_stage_definitions():
    return [
        (0, "BASELINE", "Same modeled infrastructure"),
        (1, "CHANGE / PREPARE", "Strategy diverges"),
        (2, "TRACE", "ACDKG impact traversal"),
        (3, "COMPATIBILITY", "Protocol / trust readiness"),
        (4, "CONTROLLED CHANGE", "Proposed PQC transition"),
        (5, "VERIFY", "Post-change validation"),
    ]

def simulation_plan_steps(row, target, result):
    affected=len(impacted_components(row.id)); depth=max(dependency_depths(row.id).values(),default=0)
    tech=technical_dependencies(row.id)
    protocols=[n for n,r in tech if r=="uses_protocol"]
    libs=[n for n,r in tech if r=="uses_library"]
    steps=[
        ("Dependency validation",f"Confirm {affected} modeled affected component(s) across depth {depth}."),
        ("Compatibility preparation",f"Validate {row.protocol} support and downstream service continuity."),
    ]
    if row["type"]=="Certificate":
        steps.insert(1,("Trust / PKI preparation","Validate certificate lifecycle and trust-chain dependencies."))
    if protocols:
        steps.append(("Protocol validation",f"Validate protocol compatibility: {', '.join(protocols)}."))
    if libs:
        steps.append(("Library validation",f"Validate library support: {', '.join(libs)}."))
    steps.extend([
        ("Controlled PQC change",f"Model {row.algorithm} → {target} for the {row.crypto_role.lower()} role."),
        ("Post-change verification","Revalidate dependent services, trust relationships and inventory."),
    ])
    # Keep the sequence bounded and deterministic for the UI.
    seen=set(); out=[]
    for title,detail in steps:
        if title not in seen:
            seen.add(title); out.append((title,detail))
    return out[:7]

def simulation_nodes_edges(asset_id):
    depths=dependency_depths(asset_id)
    nodes=set([asset_id]) | set(depths.keys())
    technical=technical_dependencies(asset_id)
    nodes |= {n for n,_ in technical if n in G.nodes}
    edges=[]
    for u,v,d in G.edges(data=True):
        rel=d.get("relation")
        if u in nodes and v in nodes and (rel in {"depends_on","uses_crypto_asset","protected_by","uses_protocol","uses_library","uses_service"}):
            edges.append((u,v,rel))
    return nodes,edges,depths,technical

def simulation_topology_figure(asset_id, step, mode, target):
    nodes,edges,depths,technical=simulation_nodes_edges(asset_id)
    if not nodes:
        return go.Figure()
    # Deterministic layered layout: the selected crypto asset is the anchor;
    # dependency depth moves outward, technical context stays to the side.
    pos={}
    pos[asset_id]=(0.0,0.0)
    by_depth={}
    for n,d in depths.items(): by_depth.setdefault(d,[]).append(n)
    for d,arr in sorted(by_depth.items()):
        arr=sorted(arr); span=max(2.2,1.5*len(arr));
        xs=np.linspace(-span/2,span/2,len(arr)) if len(arr)>1 else [0]
        y=0.85+d*0.78
        for x,n in zip(xs,arr): pos[n]=(float(x),float(y))
    technical_nodes=[n for n,_ in technical if n in nodes and n not in pos]
    for i,n in enumerate(sorted(set(technical_nodes))):
        pos[n]=(2.65,0.35+i*0.72)
    # Any remaining context node gets a stable fallback position.
    remaining=[n for n in sorted(nodes) if n not in pos]
    for i,n in enumerate(remaining): pos[n]=(-2.65,0.35+i*0.72)

    paths=asset_paths(asset_id)
    path_edges=set()
    for path in paths:
        for a,b in zip(path[:-1],path[1:]):
            path_edges.add((a,b))
    traversal_nodes={asset_id}
    if step>=1: traversal_nodes |= set(depths.keys())
    if step>=2: traversal_nodes |= set(depths.keys())
    if step>=3: traversal_nodes |= {n for n,_ in technical}
    if step>=4: traversal_nodes |= set(depths.keys())
    if mode=="planned":
        # Planned path reveals evidence progressively according to the gate sequence.
        if step==0: traversal_nodes={asset_id}
        elif step==1: traversal_nodes=set(depths.keys())|{asset_id}
        elif step==2: traversal_nodes=set(depths.keys())|{asset_id}|{n for n,_ in technical}
        else: traversal_nodes=set(nodes)
    else:
        if step==1: traversal_nodes={asset_id}
        elif step==2: traversal_nodes=set(depths.keys())|{asset_id}
        elif step>=3: traversal_nodes=set(nodes)

    edge_x=[];edge_y=[];edge_colors=[];edge_widths=[]
    for u,v,rel in edges:
        x1,y1=pos[u];x2,y2=pos[v]
        edge_x += [x1,x2,None]; edge_y += [y1,y2,None]
        active=(u in traversal_nodes and v in traversal_nodes)
        if rel=="depends_on":
            edge_colors.append("#4fc9ff" if active else "#254455"); edge_widths.append(3.2 if active else 1.0)
        else:
            edge_colors.append("#8b6cff" if active else "#283b49"); edge_widths.append(2.2 if active else 0.8)
    # Plotly line traces cannot vary width/color per segment in one trace, so draw edges individually.
    fig=go.Figure()
    for u,v,rel in edges:
        x1,y1=pos[u];x2,y2=pos[v];active=(u in traversal_nodes and v in traversal_nodes)
        col="#4fc9ff" if rel=="depends_on" and active else "#8b6cff" if active else "#263f4d"
        width=3.4 if active and rel=="depends_on" else 2.1 if active else .9
        fig.add_trace(go.Scatter(x=[x1,x2],y=[y1,y2],mode="lines",line=dict(color=col,width=width,dash="solid" if rel=="depends_on" else "dot"),hoverinfo="skip",showlegend=False))
    xs=[];ys=[];texts=[];colors=[];sizes=[];hover=[]
    for n in sorted(nodes):
        x,y=pos[n];xs.append(x);ys.append(y)
        is_asset=n==asset_id; active=n in traversal_nodes
        if is_asset:
            col="#65d4ff" if step>=1 else "#315d72"; size=25
        elif n in depths:
            col="#36b9ef" if active else "#294553"; size=18 if active else 13
        else:
            col="#9a7cff" if active else "#394054"; size=15 if active else 11
        colors.append(col);sizes.append(size)
        label=str(n); texts.append(label)
        depth_label="asset" if is_asset else f"dependency depth {depths.get(n,'technical context')}"
        hover.append(f"{label}<br>{depth_label}")
    fig.add_trace(go.Scatter(x=xs,y=ys,mode="markers+text",text=texts,textposition="top center",textfont=dict(size=9,color="#c9dbe5"),marker=dict(size=sizes,color=colors,line=dict(color="#b9eaff",width=0.5)),hovertext=hover,hovertemplate="%{hovertext}<extra></extra>",showlegend=False))
    # Small anchor label for the proposed target.
    if asset_id in pos:
        ax,ay=pos[asset_id]
        fig.add_annotation(x=ax,y=ay-0.32,text=f"{target}" if step>=1 else "CURRENT",showarrow=False,font=dict(size=8,color="#79cfff"),bgcolor="#07131c",bordercolor="#28536a",borderpad=3)
    fig.update_layout(height=390,margin=dict(l=15,r=15,t=10,b=10),paper_bgcolor="#071119",plot_bgcolor="#071119",xaxis=dict(visible=False,range=[-3.4,3.4]),yaxis=dict(visible=False,range=[-0.55,max(2.8,0.9+max(depths.values(),default=0)*.78+1.2)]),showlegend=False,hoverlabel=dict(bgcolor="#0b1a24",font_color="#d9eef7"))
    return fig

def simulation_state_copy(row,target,result,step,mode):
    affected=len(impacted_components(row.id)); depth=max(dependency_depths(row.id).values(),default=0)
    checks=result.get("checks",[]) if result else []
    conflicts=result.get("conflicts",[]) if result else []
    if mode=="planned":
        states=[
            ("BASELINE","Baseline infrastructure established.","No migration state changed."),
            ("DEPENDENCY VALIDATION","ACDKG dependencies are established before the change.",f"{affected} affected component(s) · depth {depth}."),
            ("COMPATIBILITY PREPARATION","Technical and trust relationships are prepared for validation.",f"{len(checks)} validation requirement(s) generated."),
            ("CONTROLLED CHANGE",f"Modeled transition {row.algorithm} → {target}.","No production configuration is modified."),
            ("REVALIDATION","Dependent paths are evaluated after the modeled change.","Continuity and inventory checks remain required."),
            ("COMMIT / HOLD","Simulation reaches a decision gate.","A real deployment would require external validation before commit."),
        ]
    else:
        states=[
            ("BASELINE","Baseline infrastructure established.","Same ACDKG topology as the planned path."),
            ("IMMEDIATE CHANGE",f"Modeled transition {row.algorithm} → {target} is introduced first.","Dependency consequences are evaluated after the change."),
            ("IMPACT DISCOVERY","ACDKG traversal reveals the reachable dependency surface.",f"{affected} affected component(s) · depth {depth}."),
            ("COMPATIBILITY CHECK","Compatibility conditions are evaluated after the change.",f"{len(conflicts)} modeled condition(s) require review."),
            ("VALIDATION / RECOVERY","The path reaches validation rather than assuming success.","Any real incompatibility would require controlled recovery."),
            ("FINAL MODELED STATE","Both strategies converge on a validation-aware conclusion.","The comparison is not a production outcome prediction."),
        ]
    return states[step]

def simulation_event_rows(row,target,result,step,mode):
    affected=len(impacted_components(row.id)); depth=max(dependency_depths(row.id).values(),default=0)
    role=row.crypto_role
    common=[
        ("00:01","LOAD",f"{row.id} · {row.algorithm} → {target}"),
        ("00:02","ACDKG",f"{affected} affected component(s), max depth {depth}"),
        ("00:03","ROLE",f"{role} transition checked against role-aware PQC target"),
    ]
    if step>=1 and mode=="unprepared": common.append(("00:04","CHANGE","Proposed change introduced before preparation"))
    if step>=1 and mode=="planned": common.append(("00:04","PLAN","Dependency validation gate activated"))
    if step>=2 and mode=="planned": common.append(("00:05","COMPAT","Compatibility preparation gate activated"))
    if step>=2 and mode=="unprepared": common.append(("00:05","TRACE","Dependency traversal activated"))
    if step>=3: common.append(("00:06","SIM","Modeled consequence state evaluated"))
    if step>=4: common.append(("00:07","VERIFY","Post-change validation remains required"))
    return common[-6:]


def simulation_v2_steps():
    return [
        ("BASELINE", "Current modeled state"),
        ("IMPACT", "Trace the dependency surface"),
        ("PREPARE", "Establish validation gates"),
        ("CHANGE", "Model the PQC transition"),
        ("VALIDATE", "Evaluate post-change checks"),
        ("DECISION", "Reach the migration gate"),
    ]

def simulation_v2_graph(asset_id, step, mode, target):
    nodes,edges,depths,technical=simulation_nodes_edges(asset_id)
    if not nodes:
        return go.Figure()
    owners=set(direct_owner(asset_id))
    tech_nodes={n for n,_ in technical if n in nodes}
    pos={asset_id:(0,-1.9)}
    owner_list=sorted(owners)
    xs=np.linspace(-1.0,1.0,len(owner_list)) if len(owner_list)>1 else [0]
    for x,n in zip(xs,owner_list): pos[n]=(float(x),-0.72)
    depth_groups={}
    for n,d in depths.items():
        if n in owners: continue
        depth_groups.setdefault(d,[]).append(n)
    for d,arr in sorted(depth_groups.items()):
        arr=sorted(arr); xs=np.linspace(-1.15,1.15,len(arr)) if len(arr)>1 else [0]
        for x,n in zip(xs,arr): pos[n]=(float(x),0.25+(d-1)*0.82)
    tech_list=sorted(tech_nodes)
    if tech_list:
        ys=np.linspace(-.45,.95,len(tech_list)) if len(tech_list)>1 else [0.25]
        for y,n in zip(ys,tech_list): pos[n]=(2.35,float(y))
    for i,n in enumerate(sorted(nodes)):
        if n not in pos: pos[n]=(-2.35,0.2+i*.55)

    guided=(mode=="guided")
    changed=(step>=3 if guided else step>=1)

    # The visual state deliberately changes by phase so the user can SEE the
    # simulation progressing rather than merely reading a different sentence.
    if guided:
        active={asset_id}
        if step>=1: active |= set(owners) | set(depths)
        if step>=2: active |= tech_nodes
        if step>=3: active |= set(depths) | tech_nodes
        review_nodes=set()
        phase_color="#49c7f1"
        phase_label=["CURRENT STATE","DEPENDENCY IMPACT","PREPARATION GATES","PQC TRANSITION","POST-CHANGE VALIDATION","DECISION GATE"][step]
        phase_note=[
            "No migration state changed",
            "Dependency path is being traced",
            "Technical interfaces become validation gates",
            "Cryptographic state transition is modeled",
            "Affected surface is revalidated",
            "Evidence is ready for the next migration decision",
        ][step]
    else:
        active={asset_id}
        if step>=2: active |= set(owners) | set(depths)
        if step>=3: active |= tech_nodes
        review_nodes=set()
        if step>=2: review_nodes |= set(owners) | set(depths)
        if step>=3: review_nodes |= tech_nodes
        if step>=4: review_nodes |= set(owners) | set(depths) | tech_nodes
        phase_color="#d7a85d" if step>=1 else "#49c7f1"
        phase_label=["CURRENT STATE","CHANGE INTRODUCED","IMPACT DISCOVERY","REMEDIATION REVIEW","POST-CHANGE VALIDATION","DECISION GATE"][step]
        phase_note=[
            "No migration state changed",
            "Change occurs before preparation",
            "Dependencies are discovered after the change",
            "Compatibility and continuity review is now required",
            "Remaining review gates are evaluated",
            "Evidence is ready for a remediation-aware decision",
        ][step]

    fig=go.Figure()
    # Edges: baseline is deliberately quiet; the current causal path becomes
    # brighter as the simulation advances.
    for u,v,rel in edges:
        if u not in pos or v not in pos: continue
        active_edge=(u in active and v in active)
        review_edge=(u in review_nodes or v in review_nodes) and not guided and step>=2
        if rel=="depends_on":
            col="#d7a85d" if review_edge else ("#48c7f1" if active_edge else "#29424f")
            width=3.8 if review_edge else (3.4 if active_edge else 1.0)
            dash="solid"
        else:
            col="#d7a85d" if review_edge else ("#8d78df" if active_edge else "#2c3b47")
            width=3.0 if review_edge else (2.4 if active_edge else .8)
            dash="dot"
        fig.add_trace(go.Scatter(x=[pos[u][0],pos[v][0]],y=[pos[u][1],pos[v][1]],mode="lines",line=dict(color=col,width=width,dash=dash),hoverinfo="skip",showlegend=False))

    # Soft halos make each state transition visually obvious without adding
    # decorative animation or changing the underlying topology.
    halo_nodes=set(active) if step>0 else {asset_id}
    if not guided and step>=2:
        halo_nodes |= review_nodes
    hx=[];hy=[];hc=[];hs=[]
    for n in sorted(halo_nodes):
        x,y=pos[n];hx.append(x);hy.append(y)
        if n in review_nodes and not guided: hc.append("#d7a85d")
        else: hc.append("#49c7f1")
        hs.append(42 if n==asset_id else 30)
    if hx:
        fig.add_trace(go.Scatter(x=hx,y=hy,mode="markers",marker=dict(size=hs,color=hc,opacity=.09,line=dict(width=0)),hoverinfo="skip",showlegend=False))

    xs=[];ys=[];texts=[];colors=[];sizes=[];hovers=[]
    for n in sorted(nodes):
        x,y=pos[n];xs.append(x);ys.append(y)
        is_asset=n==asset_id; active_n=n in active; review_n=n in review_nodes
        if is_asset:
            col="#58d0f5" if changed else "#487d96"; size=35
            status=(str(target) if changed else str(G.nodes[asset_id].get('algorithm','CURRENT')))
        elif n in owners:
            col="#d7a85d" if review_n and not guided else ("#39b4df" if active_n else "#31515f")
            status="REVIEW" if review_n and not guided else "OWNER"
            size=24 if active_n else 18
        elif n in depths:
            col="#d7a85d" if review_n and not guided else ("#44b9e6" if active_n else "#324651")
            status="REVIEW" if review_n and not guided else f"DEPTH {depths[n]}"
            size=20 if active_n else 14
        else:
            col="#d7a85d" if review_n and not guided else ("#9a82e6" if active_n else "#39414e")
            status="REVIEW" if review_n and not guided else "TECHNICAL"
            size=19 if active_n else 13
        colors.append(col);sizes.append(size)
        label=str(n)
        # Only the currently consequential nodes get status suffixes; this
        # prevents the graph from becoming a wall of repeated labels.
        if is_asset and changed:
            label=f"{n} → {target}"
        elif not guided and review_n and step>=2:
            label=f"{n} · REVIEW"
        elif guided and step in (1,2) and n in active and n!=asset_id:
            label=f"{n} · {'DEPENDENCY' if n in depths or n in owners else 'VALIDATE'}"
        texts.append(label)
        role="selected crypto asset" if is_asset else ("direct owner" if n in owners else (f"dependency depth {depths[n]}" if n in depths else "technical context"))
        hovers.append(f"{html.escape(str(n))}<br>{html.escape(role)}<br>State: {html.escape(status)}")
    fig.add_trace(go.Scatter(x=xs,y=ys,mode="markers+text",text=texts,textposition="top center",textfont=dict(size=11,color="#d4e7ef"),marker=dict(size=sizes,color=colors,line=dict(color="#0b151d",width=1.4)),hovertext=hovers,hovertemplate="%{hovertext}<extra></extra>",showlegend=False))

    ax,ay=pos[asset_id]
    fig.add_annotation(x=ax,y=ay-.46,text=(str(target) if changed else str(G.nodes[asset_id].get('algorithm', 'CURRENT'))),showarrow=False,font=dict(size=10,color="#8bdfff"),bgcolor="#07131b",bordercolor="#2d647c",borderpad=4)
    fig.add_annotation(x=-2.55,y=1.82,text=phase_label,showarrow=False,xanchor="left",font=dict(size=11,color=phase_color),bgcolor="#0a1820",bordercolor=phase_color,borderpad=5)
    fig.add_annotation(x=-2.55,y=1.43,text=phase_note,showarrow=False,xanchor="left",font=dict(size=9,color="#8fa9b8"))
    if tech_nodes:
        fig.add_annotation(x=2.35,y=1.55,text=("REVIEW / REMEDIATION" if (not guided and step>=3) else "TECHNICAL VALIDATION"),showarrow=False,font=dict(size=10,color="#d7a85d" if not guided and step>=3 else "#a18be2"),bgcolor="#0a151d",bordercolor="#70582f" if not guided and step>=3 else "#51436f",borderpad=4)
    fig.update_layout(height=470,margin=dict(l=8,r=8,t=16,b=8),paper_bgcolor="#071119",plot_bgcolor="#071119",xaxis=dict(visible=False,range=[-2.9,2.9]),yaxis=dict(visible=False,range=[-2.55,2.12]),showlegend=False,hoverlabel=dict(bgcolor="#0b1a24",font_color="#d9eef7"))
    return fig

def simulation_v2_content(row,target,result,step,mode):
    affected=len(impacted_components(row.id)); depth=max(dependency_depths(row.id).values(),default=0)
    checks=result.get("checks",[]) if result else []
    conflicts=result.get("conflicts",[]) if result else []
    tech=technical_dependencies(row.id)
    protocols=[n for n,r in tech if r=="uses_protocol"]
    libs=[n for n,r in tech if r=="uses_library"]
    guided=(mode=="guided")

    # The same modeled evidence is used in both paths. Only the order of
    # evidence/validation gates changes. Direct migration never fabricates an
    # outage; it creates post-change review/remediation gates from actual ACDKG
    # evidence.
    direct_issues=[]
    if protocols:
        direct_issues.append("Protocol compatibility review: " + ", ".join(protocols))
    if libs:
        direct_issues.append("Cryptographic library support review: " + ", ".join(libs))
    if row["type"]=="Certificate":
        direct_issues.append("Certificate / trust-chain validation")
    if affected:
        direct_issues.append(f"{affected} dependent component(s) require continuity validation")

    if guided:
        titles=[
            ("BASELINE ESTABLISHED", "The current modeled infrastructure is loaded before any cryptographic state transition."),
            ("DEPENDENCY IMPACT IDENTIFIED", f"NEXORA traces {affected} affected component(s) across {depth} dependency level(s) before the proposed change."),
            ("PREPARATION GATES ESTABLISHED", f"{len(checks)} validation requirement(s) are brought forward before the modeled cryptographic transition."),
            ("CRYPTOGRAPHIC CHANGE MODELED", f"The proposed {row.algorithm} → {target} transition is introduced after dependency and compatibility preparation."),
            ("POST-CHANGE VALIDATION", "The prepared dependency surface remains visible while the required post-change checks are evaluated."),
            ("VALIDATION-AWARE DECISION", "The sequence reaches a decision gate with evidence and validation requirements ready for external verification."),
        ]
        why=[
            "The simulation begins from the same modeled infrastructure used by TRACE and PLAN.",
            f"The ACDKG identifies the reachable impact surface: {affected} component(s), maximum depth {depth}.",
            "Preparation is treated as a gate before the cryptographic state changes.",
            "The cryptographic transition is modeled only after the dependency surface has been prepared.",
            "Post-change checks are evaluated without claiming real-world interoperability.",
            "NEXORA stops at a validation-aware decision rather than claiming production success.",
        ][step]
        return titles[step][0],titles[step][1],affected,depth,checks,[],why

    # Immediate/direct path: the consequence is deliberately different.
    titles=[
        ("BASELINE ESTABLISHED", "The same modeled infrastructure is loaded. No dependency preparation has been performed yet."),
        ("IMMEDIATE CHANGE INTRODUCED", f"The proposed {row.algorithm} → {target} transition is modeled before the dependency surface has been prepared."),
        ("IMPACT DISCOVERED AFTER CHANGE", f"The ACDKG now exposes {affected} affected component(s) across {depth} dependency level(s) after the transition was introduced."),
        ("REMEDIATION GATES REQUIRED", f"{len(direct_issues)} post-change review condition(s) are now required because compatibility preparation was deferred."),
        ("POST-CHANGE VALIDATION", "The model reaches validation with unresolved review gates; a real incompatibility would require controlled remediation and re-test."),
        ("REMEDIATION-AWARE DECISION", "The direct sequence reaches the same final decision boundary, but with additional post-change review/remediation work exposed."),
    ]
    why=[
        "The direct path starts from the same evidence but intentionally changes the cryptographic state first.",
        "The change is introduced before NEXORA has established the dependency and compatibility gates.",
        "Impact is discovered after the change instead of being prepared beforehand.",
        "Actual protocol, library, certificate and dependency evidence becomes post-change review work.",
        "The model does not assume failure; it surfaces the validation and remediation work that remains.",
        "The prototype records a controlled decision point rather than claiming a production outage or success.",
    ][step]
    return titles[step][0],titles[step][1],affected,depth,checks,direct_issues,why


if st.session_state.stage=="OVERVIEW":
    pcase=SCENARIOS[st.session_state.selected_environment]
    selected=st.session_state.get("trace_asset")
    target=st.session_state.get("pqc_target")
    preview=case_change_preview(selected,target) if selected in df.id.tolist() else None
    vulnerable=sum(str(a) in ALGORITHM_VULNERABILITY for a in df["algorithm"].tolist())
    roles=df["crypto_role"].nunique()

    st.markdown(f"""<div class='nx-case-brief-hero'>
      <div class='nx-case-brief-kicker'>01 · CASE COMMAND BRIEF · {html.escape(str(pcase['case']))}</div>
      <h2>{html.escape(st.session_state.selected_environment)}</h2>
      <p>{html.escape(str(pcase['summary']))}</p>
      <div class='nx-case-question'><span>THE CASE QUESTION</span><b>If cryptography protecting {html.escape(str(pcase['focus']).lower())} changes, what surrounding infrastructure must be understood before migration planning?</b></div>
    </div>""",unsafe_allow_html=True)

    st.markdown(f"""<div class='nx-case-dna'>
      <div class='nx-case-dna-card'><span>INFRASTRUCTURE</span><b>{len(COMPONENTS)}</b><small>modeled components in this controlled case</small></div>
      <div class='nx-case-dna-card'><span>CRYPTO SURFACE</span><b>{len(df)}</b><small>cryptographic assets represented</small></div>
      <div class='nx-case-dna-card'><span>QUANTUM-VULNERABLE</span><b>{vulnerable}</b><small>assets using modeled classical public-key algorithms</small></div>
      <div class='nx-case-dna-card'><span>CRYPTO ROLES</span><b>{roles}</b><small>digital signature and key-establishment roles represented</small></div>
    </div>""",unsafe_allow_html=True)

    st.markdown("""
    <div class='nx-case-insight'>
      <div class='nx-case-insight-label'>NEXORA INVESTIGATION PRINCIPLE</div>
      <div class='nx-case-insight-grid'>
        <div><b>INVENTORY</b><span>What exists and where cryptography is used.</span></div>
        <div><b>ACDKG</b><span>What is connected and what can be affected by a change.</span></div>
        <div><b>PLANNING</b><span>What must be prepared, validated and rechecked before migration.</span></div>
      </div>
    </div>
    """,unsafe_allow_html=True)

    st.markdown("""<div class='nx-case-section-head'><div><div class='eyebrow'>CRYPTO SURFACE FLOW</div><h3>Where cryptography sits inside the case</h3></div><p>Interactive flow from infrastructure grouping → cryptographic role → current algorithm. This is a surface view, not the ACDKG dependency graph.</p></div>""",unsafe_allow_html=True)
    st.markdown("<div class='nx-case-surface'>",unsafe_allow_html=True)
    st.plotly_chart(case_crypto_surface_figure(),width="stretch",config={"displayModeBar":False})
    st.markdown("<div class='nx-case-surface-note'><b>How to read it:</b> wider flows mean more modeled assets follow that category. Hover a flow or node for the exact asset count.</div></div>",unsafe_allow_html=True)

    # Live selected-asset what-if preview. It deliberately stops before full dependency graph reasoning.
    st.markdown("""<div class='nx-case-section-head'><div><div class='eyebrow'>LIVE CHANGE PREVIEW</div><h3>What changes when you select an investigation asset?</h3></div><p>The controls above are live. Selecting an asset changes this preview immediately; the full relationship investigation remains in TRACE.</p></div>""",unsafe_allow_html=True)
    if preview:
        row,depths,affected,tech,domains=preview
        target_text=str(target) if target else (PQC_OPTIONS.get(str(row.crypto_role),[str(row['Suggested PQC'])])[0] if PQC_OPTIONS.get(str(row.crypto_role)) else str(row['Suggested PQC']))
        standard=PQC_STANDARD.get(target_text,"PQC direction")
        domain_html="".join(f"<span class='nx-live-pill affected'>{html.escape(d)}</span>" for d in domains) or "<span class='nx-live-pill'>owner only</span>"
        st.markdown(f"""<div class='nx-change-lab'>
          <div class='nx-change-state'>
            <div class='eyebrow'>SELECTED ASSET · LIVE</div>
            <h3>{html.escape(str(row.id))} · {html.escape(str(row['name']))}</h3>
            <div class='sub'>{html.escape(str(row.crypto_role))} · {html.escape(str(row.protocol))} · owner: {html.escape(str(row.owner))}</div>
            <div class='nx-algo-swap'>
              <div class='nx-algo-box'><span>CURRENT</span><b>{html.escape(str(row.algorithm))}</b><small>classical cryptography in the modeled case</small></div>
              <div class='nx-swap-arrow'>→</div>
              <div class='nx-algo-box target'><span>PQC DIRECTION</span><b>{html.escape(target_text)}</b><small>{html.escape(standard)}</small></div>
            </div>
            <div class='nx-live-pill-row'>{domain_html}</div>
          </div>
          <div class='nx-change-impact'>
            <div class='nx-impact-head'><div class='eyebrow'>MODELED CHANGE BOUNDARY</div><h3>What NEXORA will investigate next</h3></div>
            <div class='nx-impact-grid'>
              <div><span>OWNER</span><b>{html.escape(str(row.owner))}</b><small>direct cryptographic owner</small></div>
              <div><span>IMPACTED</span><b>{len(affected)}</b><small>modeled components in dependency traversal</small></div>
              <div><span>DEPTH</span><b>{max(depths.values(),default=0)}</b><small>maximum dependency depth</small></div>
              <div><span>TECHNICAL LINKS</span><b>{len(tech)}</b><small>protocol / library / service links</small></div>
            </div>
            <div style='padding:15px 18px 17px'><div class='nx-live-pill-row'><span class='nx-live-pill'>NEXT · TRACE FULL DEPENDENCY</span><span class='nx-live-pill'>THEN · ASSESS IMPACT</span><span class='nx-live-pill'>THEN · PLAN CHANGE</span></div></div>
          </div>
        </div>""",unsafe_allow_html=True)
    else:
        st.markdown("""<div class='nx-live-empty'><b>No investigation target selected.</b><br>Select a cryptographic asset in the global investigation controls above. The Case page will immediately populate the current → PQC transition and modeled change boundary without duplicating the full ACDKG.</div>""",unsafe_allow_html=True)

    # Comparative case lens: same measurement, three controlled environments.
    st.markdown("""<div class='nx-case-section-head'><div><div class='eyebrow'>CONTROLLED CASE COMPARISON</div><h3>How the three environments differ</h3></div><p>Use one measurement at a time. These are modeled scenario characteristics, not real enterprise benchmarks.</p></div>""",unsafe_allow_html=True)
    metric_options=["Crypto assets","Infrastructure components","ACDKG relationships","Quantum-vulnerable assets","Average CMIS"]
    metric=st.radio("Comparison lens",metric_options,key="case_compare_metric",horizontal=True,label_visibility="collapsed")
    comp_records=[]
    for name in SCENARIOS:
        tdf,tg,tcomp=build_scenario_data(name)
        if metric=="Crypto assets": val=len(tdf)
        elif metric=="Infrastructure components": val=len(tcomp)
        elif metric=="ACDKG relationships": val=tg.number_of_edges()
        elif metric=="Quantum-vulnerable assets": val=sum(str(r["algorithm"]) in ALGORITHM_VULNERABILITY for _,r in tdf.iterrows())
        else:
            vals=[min(round(ALGORITHM_VULNERABILITY.get(r["algorithm"],2)*8+r["criticality"]*6+r["exposure"]*5+r["complexity"]*4),100) for _,r in tdf.iterrows()]
            val=round(float(np.mean(vals)),1) if vals else 0
        comp_records.append((name,val))
    active_val=next((v for n,v in comp_records if n==st.session_state.selected_environment),0)
    values=[v for _,v in comp_records]; low,high=min(values),max(values)
    if high==low: reading="All three controlled cases have the same modeled value for this lens."
    elif active_val==high: reading="The active case has the highest modeled value for this selected lens."
    elif active_val==low: reading="The active case has the lowest modeled value for this selected lens."
    else: reading="The active case sits between the other two controlled scenario values."
    st.markdown(f"<div class='nx-compare-lens'><div><span>ACTIVE CASE</span><b>{html.escape(st.session_state.selected_environment)}</b><small>{html.escape(metric)}</small></div><div><span>MODELED VALUE</span><b>{active_val}</b><small>active case</small></div><div><span>CASE RANGE</span><b>{low} - {high}</b><small>three deterministic scenarios</small></div><div class='reading'><span>READING</span><b>{html.escape(reading)}</b><small>descriptive comparison, not an enterprise benchmark</small></div></div>",unsafe_allow_html=True)
    st.markdown("<div class='nx-case-compare'>",unsafe_allow_html=True)
    st.plotly_chart(case_comparison_figure(metric),width="stretch",config={"displayModeBar":False})
    st.markdown(f"<div class='nx-compare-caption'><b>{html.escape(metric)}:</b> computed directly from the three deterministic NEXORA case models. Change the lens above to inspect another system characteristic without changing the investigation target.</div></div>",unsafe_allow_html=True)

    # The journey is now a compact contract, not another explanation of the architecture.
    st.markdown("""<div class='nx-case-section-head'><div><div class='eyebrow'>INVESTIGATION CONTRACT</div><h3>What this page hands to the next stages</h3></div><p>Each stage owns a different question, so later pages do not need to repeat this briefing.</p></div>""",unsafe_allow_html=True)
    journey=[("01","DISCOVER","Inventory","What exists?"),("02","TRACE","ACDKG","What depends on it?"),("03","ASSESS","Impact + AI","Why does it matter?"),("04","PLAN","Sequence","What must happen first?"),("05","SIMULATE","What-if","What happens after the change?")]
    st.markdown("<div class='nx-case-journey'>"+"".join(f"<div class='nx-journey-step {'active' if i==1 else ''}'><span>{n} · {tag}</span><b>{out}</b><small>{q}</small></div>" for i,(n,tag,out,q) in enumerate(journey))+"</div>",unsafe_allow_html=True)
    st.markdown("<div class='nx-case-footnote'><b>Boundary:</b> this case is a controlled academic model. NEXORA's role is evidence-driven reasoning, migration planning and controlled simulation; it does not execute cryptographic changes on production infrastructure.</div>",unsafe_allow_html=True)

    if st.button("Begin discovery →",type="primary",key="nx_case_next",width="stretch"):
        go_stage("DISCOVERY")

# ============================================================
# 02 DISCOVERY
# ============================================================
elif st.session_state.stage=="DISCOVERY":
    render_page_intro("02","DISCOVER","Find what exists before anything changes","NEXORA establishes the evidence base first: infrastructure, cryptographic assets and the relationships that connect them.")
    v19_finding("DISCOVERY FINDING",f"NEXORA identified {len(df)} cryptographic assets across {len(COMPONENTS)} modeled infrastructure components and {G.number_of_edges()} ACDKG relationships.")

    # Infrastructure evidence + immediate interpretation
    c1,c2=st.columns([1.62,.78],gap="large")
    with c1:
        st.markdown("<div class='v19-table-caption'><div><h3>Infrastructure inventory</h3><p>Click a row to focus the investigation on that component.</p></div><span class='v19-table-note'>SELECTABLE EVIDENCE</span></div>",unsafe_allow_html=True)
        comp=COMPONENTS.copy();comp.columns=["Asset ID","Component","Type","Status","Crypto Dependency","Protocol"]
        comp_display=comp.copy(); comp_display["Investigation"]=["CONTEXT"]*len(comp_display)
        chosen_component=v21_selectable_dataframe(comp_display,"v21_infrastructure_table","Component","infrastructure_asset",height=285)
    with c2:
        if chosen_component:
            cr=COMPONENTS.loc[COMPONENTS.iloc[:,1]==chosen_component].iloc[0]
            related=df[df.owner==chosen_component]
            related_names=", ".join(related.id.astype(str).tolist()) if len(related) else "No direct crypto asset recorded"
            st.markdown(f"<div class='v21-insight-panel'><span>SELECTED COMPONENT</span><h3>{html.escape(str(chosen_component))}</h3><p>This component provides context for the dependency investigation.</p><div class='v21-insight-line'><b>Type</b><span>{html.escape(str(cr.iloc[2]))}</span></div><div class='v21-insight-line'><b>Protocol</b><span>{html.escape(str(cr.iloc[5]))}</span></div><div class='v21-insight-line'><b>Owned crypto</b><span>{html.escape(related_names)}</span></div><p class='v21-insight-emphasis'>Selecting infrastructure helps connect the raw inventory to the cryptographic assets that NEXORA will trace.</p></div>",unsafe_allow_html=True)
        else:
            app_count=int((COMPONENTS['Type']=='Application').sum());svc_count=int(COMPONENTS['Type'].isin(['Service','Security Service']).sum())
            st.markdown(f"<div class='v21-insight-panel'><span>READ THIS FIRST</span><h3>The inventory is the map, not the conclusion.</h3><p>{app_count} application-layer components and {svc_count} service/security components form the operational context around the cryptographic assets.</p><p class='v21-insight-emphasis'>Select a row when you want to see how one infrastructure component connects to the cryptographic investigation.</p></div>",unsafe_allow_html=True)

    # Crypto evidence + selectable investigation target
    c1,c2=st.columns([1.62,.78],gap="large")
    with c1:
        st.markdown("<div class='v19-table-caption'><div><h3>Cryptographic inventory</h3><p>Select an asset to immediately reveal why it deserves investigation.</p></div><span class='v19-table-note'>MIGRATION EVIDENCE</span></div>",unsafe_allow_html=True)
        inv=df[["id","name","type","algorithm","crypto_role","protocol","owner","CMIS","Risk","Suggested PQC"]].copy()
        inv.columns=["Asset","Name","Type","Current algorithm","Crypto role","Protocol","Owner","CMIS","Risk","PQC direction"]
        inv["Investigation signal"]=[v21_inventory_signal(df.loc[df.id==aid].iloc[0]) for aid in inv["Asset"]]
        chosen_asset=v21_selectable_dataframe(inv,"v21_crypto_table","Asset","discovery_asset",height=330)
        if chosen_asset:
            st.session_state.trace_asset=chosen_asset
    with c2:
        chosen_asset=st.session_state.get("discovery_asset")
        if chosen_asset in df.id.tolist():
            ar=df.loc[df.id==chosen_asset].iloc[0]
            affected=len(impacted_components(chosen_asset));depth=max(dependency_depths(chosen_asset).values(),default=0)
            signal=v21_inventory_signal(ar)
            st.markdown(f"<div class='v21-insight-panel selected'><span>USER-SELECTED INVESTIGATION · {html.escape(signal)}</span><h3>{html.escape(str(ar['name']))}</h3><div class='v21-big-pair'><b>{html.escape(str(ar.algorithm))}</b><span>{html.escape(str(ar.crypto_role))}</span></div><div class='v21-insight-line'><b>Owner</b><span>{html.escape(str(ar.owner))}</span></div><div class='v21-insight-line'><b>Impact path</b><span>{affected} components · depth {depth}</span></div><div class='v21-insight-line'><b>PQC direction</b><span>Shown as a migration direction; no target is executed here.</span></div><p class='v21-insight-emphasis'>This asset became the investigation target only because the user selected it from the discovered inventory.</p></div>",unsafe_allow_html=True)
            if st.button("Trace selected asset  →",type="primary",key="v21_inventory_trace",width="stretch"):
                st.session_state.trace_asset=chosen_asset;go_stage("ACDKG")
        else:
            st.markdown("<div class='v21-insight-panel'><span>NO INVESTIGATION TARGET SELECTED</span><h3>Discovery is complete enough to choose deliberately.</h3><p>The inventory above is the evidence base. Select one cryptographic asset to turn it into an investigation target.</p><p class='v21-insight-emphasis'>NEXORA does not assume that the highest CMIS asset is automatically the right asset for the demonstration.</p></div>",unsafe_allow_html=True)

    st.markdown("<div class='v32-bridge-caption'><span>INFRASTRUCTURE ↔ CRYPTOGRAPHIC ASSET BRIDGE</span><b>Actual case relationships: infrastructure owner → cryptographic asset.</b><small>Select an asset above to highlight its line.</small></div>",unsafe_allow_html=True)
    st.plotly_chart(infrastructure_crypto_bridge_figure(st.session_state.get('discovery_asset')),width='stretch',config={'displayModeBar':False})

    # HOST EVIDENCE — deliberately mapped to NEXORA's actual discovery layers.
    st.markdown("""
    <div class='v19-runtime'>
      <div class='v19-runtime-head'>
        <div>
          <div class='v18-eyebrow'>HOST EVIDENCE · READ ONLY</div>
          <h3>What evidence can NEXORA directly obtain from this execution host?</h3>
          <p>
            This is not a generic system-information dump. NEXORA collects only evidence
            that can support its operating-system intelligence, network intelligence and
            cryptographic discovery layers. Host evidence is supplementary to the modeled
            enterprise case and is not silently inserted into the ACDKG or AI model.
          </p>
        </div>
      </div>
    </div>
    """,unsafe_allow_html=True)

    if st.button("Collect NEXORA host evidence  →",key="v28_probe",width="stretch"):
        st.session_state.runtime_probe_error=None
        try:
            with st.status("NEXORA is collecting read-only evidence…",expanded=True) as status:
                st.write("1/5 · Execution host + OS identity")
                st.write("2/5 · Processes + persistent services")
                st.write("3/5 · Network interfaces + listening endpoints")
                st.write("4/5 · Certificates + cryptographic implementations")
                st.write("5/5 · Evidence-to-NEXORA mapping")
                st.session_state.local_evidence=local_host_evidence_fast()
                status.update(label="NEXORA host evidence collection complete",state="complete",expanded=False)
        except Exception as e:
            st.session_state.local_evidence=None
            st.session_state.runtime_probe_error=f"{type(e).__name__}: {e}"
        st.rerun()

    if st.session_state.get("runtime_probe_error"):
        st.error("NEXORA host evidence collection could not complete: "+str(st.session_state.runtime_probe_error))

    if st.session_state.local_evidence:
        ev=st.session_state.local_evidence
        interfaces=ev.get("interface_records") or []
        ports=ev.get("listening_records") or []
        proc=ev.get("process_sample") or []
        services=ev.get("service_records") or []
        certs=ev.get("certificate_records") or []
        crypto=ev.get("crypto_implementations") or []
        pycrypto=ev.get("python_crypto_packages") or []
        status_value=str(ev.get("telemetry_status","PARTIAL"))
        status_note="Core host discovery layers returned evidence." if status_value=="COMPLETE" else "One or more core discovery layers did not return usable evidence."

        st.markdown(f"""
        <div class='v27-runtime-banner'>
          <div>
            <span>NEXORA HOST EVIDENCE · READ ONLY</span>
            <h2>Evidence collected from the execution host.</h2>
            <p>Observed locally at {html.escape(str(ev.get('timestamp','—')))}. This evidence describes the machine running NEXORA; it does not claim to represent the entire enterprise.</p>
          </div>
          <div class='v27-collector-badge'>
            EVIDENCE STATUS<br>
            <b>{html.escape(status_value)}</b>
            <small>{html.escape(status_note)}</small>
          </div>
        </div>
        """,unsafe_allow_html=True)

        # The top strip now contains only NEXORA-relevant evidence counts.
        st.markdown(f"""
        <div class='v27-kpi-grid'>
          <div><span>HOST / OS</span><b>{html.escape(str(ev.get('hostname','—')))}</b><small>{html.escape(str(ev.get('os','—')))} · {html.escape(str(ev.get('architecture','—')))}</small></div>
          <div><span>PROCESSES</span><b>{html.escape(str(ev.get('processes','—')))}</b><small>Execution evidence for application/service correlation</small></div>
          <div><span>SERVICES</span><b>{html.escape(str(ev.get('services_count','—')))}</b><small>{html.escape(str(ev.get('running_services','—')))} reported running</small></div>
          <div><span>NETWORK</span><b>{len(interfaces)} interface(s)</b><small>{len(ports)} TCP listener(s) observed</small></div>
          <div><span>CERTIFICATES</span><b>{html.escape(str(ev.get('certificate_count','—')))}</b><small>Local trust / public-key metadata</small></div>
          <div><span>CRYPTO SURFACE</span><b>{len(crypto)+len(pycrypto)}</b><small>Tooling / runtime packages discoverable</small></div>
        </div>
        """,unsafe_allow_html=True)

        # Every evidence set is explicitly mapped to the NEXORA layer and its
        # current pipeline role. This prevents "random host telemetry" framing.
        evidence_rows=[
            ("01","HOST / OS IDENTITY",
             f"{ev.get('hostname','—')} · {ev.get('os','—')} · {ev.get('architecture','—')}",
             "OS INTELLIGENCE → DISCOVERY",
             "Establishes the execution platform on which software, services and cryptographic implementations operate.",
             "Grounding only · not an ACDKG edge · not a CMIS/AI feature."),
            ("02","PROCESSES + SERVICES",
             f"{len(proc)} process records · {len(services)} service records",
             "OS INTELLIGENCE → COMPONENT DISCOVERY",
             "Provides runtime and persistent-service evidence that can help identify application/service owners of cryptographic functions.",
             "Observed candidate evidence · no automatic case-component match."),
            ("03","NETWORK INTERFACES + LISTENERS",
             f"{len(interfaces)} interfaces · {len(ports)} TCP listeners",
             "NETWORK INTELLIGENCE → PROTOCOL CONTEXT",
             "Exposes local endpoints, bind addresses and owning processes where available; useful for protocol/service discovery.",
             "Local context only · no remote reachability claim · no enterprise topology claim."),
            ("04","CERTIFICATE STORE",
             f"{len(certs)} LocalMachine certificate records",
             "CRYPTOGRAPHIC DISCOVERY → ASSET INVENTORY",
             "Provides subject, issuer, validity, public-key and signature metadata without collecting private-key material.",
             "Direct crypto evidence · candidate input for ACDKG mapping."),
            ("05","CRYPTO IMPLEMENTATIONS",
             f"{len(crypto)} native tools · {len(pycrypto)} Python packages",
             "CRYPTOGRAPHIC DISCOVERY → IMPLEMENTATION SURFACE",
             "Shows cryptographic tooling/libraries discoverable on the host and therefore worth investigating during crypto-agility discovery.",
             "Presence evidence only · does not prove application usage."),
        ]
        evidence_header = """
        <div style='display:grid;grid-template-columns:1.05fr 1.15fr 1.35fr;gap:0;border-bottom:1px solid #29465b;
                    padding:14px 18px;background:#0d1922;color:#6eb8ea;font-size:.72rem;font-weight:800;
                    letter-spacing:.14em;text-transform:uppercase'>
          <div>OBSERVED EVIDENCE</div><div>NEXORA USE</div><div>ENGINEERING STATUS</div>
        </div>
        """
        evidence_body="".join(
            f"""<div style='display:grid;grid-template-columns:1.05fr 1.15fr 1.35fr;gap:0;
                    border-bottom:1px solid rgba(66,96,116,.42);padding:18px;
                    align-items:start'>
              <div style='padding-right:18px'>
                <div style='display:flex;gap:12px;align-items:center'>
                  <span style='display:inline-flex;width:28px;height:28px;border:1px solid #3f789b;border-radius:50%;
                               align-items:center;justify-content:center;color:#6eb8ea;font-size:.72rem;font-weight:800'>{n}</span>
                  <span style='color:#6eb8ea;font-size:.72rem;font-weight:800;letter-spacing:.12em'>{html.escape(title)}</span>
                </div>
                <b style='display:block;margin:10px 0 0;color:#f1f6fa;font-size:1rem'>{html.escape(value)}</b>
              </div>
              <div style='padding:0 18px;border-left:1px solid rgba(66,96,116,.42);border-right:1px solid rgba(66,96,116,.42)'>
                <span style='color:#6eb8ea;font-size:.72rem;font-weight:800;letter-spacing:.1em'>{html.escape(layer)}</span>
                <p style='margin:8px 0 0;color:#a9bfce;line-height:1.55;font-size:.88rem'>{html.escape(why)}</p>
              </div>
              <div style='padding-left:18px'>
                <span style='color:#dbe8f1;font-size:.85rem;font-weight:700'>CURRENT NEXORA ROLE</span>
                <p style='margin:8px 0 0;color:#7fa5ba;line-height:1.55;font-size:.84rem'>{html.escape(role)}</p>
              </div>
            </div>"""
            for n,title,value,layer,why,role in evidence_rows
        )
        st.markdown(
            "<div class='v28-processing-trace'>"
            "<div class='v28-trace-head'><span>NEXORA EVIDENCE MAP</span>"
            "<b>Why each observation exists — and exactly where it belongs</b></div>"+
            evidence_header+evidence_body+
            "</div>",unsafe_allow_html=True)

        st.markdown("""
        <div class='v29-evidence-purpose'>
          <div>
            <span>ENGINEERING BOUNDARY</span>
            <h3>Host evidence is an input surface — not the NEXORA decision model.</h3>
            <p>
              The modeled case, ACDKG relationships, CMIS assessment and migration planner remain
              the decision-producing layers. This host collector supplies observed evidence that can
              validate or enrich discovery. NEXORA does <b>not</b> infer an application-to-certificate
              relationship merely because both were found on the same machine.
            </p>
          </div>
          <div class='v29-evidence-scope'>
            <b>NOT CLAIMED</b>
            <strong>Enterprise discovery</strong>
            <small>No remote scanning · no packet capture · no private keys · no automatic ACDKG mapping · no production changes</small>
          </div>
        </div>
        """,unsafe_allow_html=True)

        g1,g2=st.columns([1.3,.7],gap="large")
        with g1:
            st.markdown("""
            <div class='v27-section'>
              <span>NEXORA EVIDENCE RELATIONSHIPS</span>
              <h3>Observed host evidence map</h3>
              <p>Only observations that correspond to NEXORA's OS, network or cryptographic discovery layers are shown here.</p>
            </div>
            """,unsafe_allow_html=True)
            st.plotly_chart(runtime_graph_figure(ev),width="stretch",config={"displayModeBar":False})
        with g2:
            st.markdown("""
            <div class='v27-section'>
              <span>DISCOVERY COUNTS</span>
              <h3>What the collector actually returned</h3>
              <p>Counts are evidence counts, not enterprise asset counts.</p>
            </div>
            """,unsafe_allow_html=True)
            counts=pd.DataFrame([
                ["Processes",len(proc),"OS Intelligence"],
                ["Services",len(services),"OS Intelligence"],
                ["Network interfaces",len(interfaces),"Network Intelligence"],
                ["TCP listeners",len(ports),"Network Intelligence"],
                ["Certificates",len(certs),"Cryptographic Discovery"],
                ["Native crypto tools",len(crypto),"Cryptographic Discovery"],
                ["Python crypto packages",len(pycrypto),"Cryptographic Discovery"],
            ],columns=["Observed evidence","Count","NEXORA layer"])
            st.dataframe(counts,width="stretch",hide_index=True,height=320)

        probe_rows=[]
        for label,info in (ev.get("probe_status") or {}).items():
            if not isinstance(info,dict): continue
            probe_rows.append({"Collector probe":label,"Status":info.get("status","—"),"Reason / count":info.get("reason", info.get("count", ""))})
        if probe_rows:
            st.markdown("<div class='v40-section-head' style='margin-top:18px'><span>COLLECTOR INTEGRITY</span><h3>Did each evidence source actually return?</h3><p>This is deliberately separate from the NEXORA interpretation layer: it shows whether the local acquisition probe succeeded.</p></div>",unsafe_allow_html=True)
            st.dataframe(pd.DataFrame(probe_rows),width="stretch",hide_index=True,height=min(310,90+42*len(probe_rows)))

        # Detailed evidence is grouped by the NEXORA layer it supports.
        st.markdown("""
        <div class='v27-section'>
          <span>OS INTELLIGENCE</span>
          <h3>Execution components NEXORA can observe</h3>
          <p>These records establish what is running or installed on the execution host. They are evidence for discovery, not proof of cryptographic use.</p>
        </div>
        """,unsafe_allow_html=True)
        o1,o2=st.columns([1.35,.65],gap="large")
        with o1:
            ptable=pd.DataFrame(proc)
            stable=pd.DataFrame(services)
            st.markdown("<div class='v40-table-label'><span>OBSERVED PROCESS RECORDS</span><b>Runtime components</b></div>",unsafe_allow_html=True)
            st.dataframe(ptable if not ptable.empty else pd.DataFrame([{"Status":"No process evidence returned"}]),width="stretch",hide_index=True,height=min(500,150+max(len(ptable),1)*34))
            st.markdown("<div class='v40-table-label' style='margin-top:14px'><span>OBSERVED SERVICE RECORDS</span><b>Persistent OS components</b></div>",unsafe_allow_html=True)
            st.dataframe(stable if not stable.empty else pd.DataFrame([{"Status":"No service evidence returned"}]),width="stretch",hide_index=True,height=min(500,150+max(len(stable),1)*34))
        with o2:
            st.markdown("<div class='v40-purpose-panel'><span>NEXORA USE</span><h3>OS Intelligence</h3><p><b>Question:</b> what execution and persistent service components exist on this host?</p><p><b>Feeds:</b> discovery candidate evidence and possible owner correlation.</p><p><b>Not claimed:</b> a process name alone does not prove which cryptographic algorithm or certificate it uses.</p><strong>CURRENT ROLE</strong><small>Observed candidate evidence · no automatic ACDKG mapping</small></div>",unsafe_allow_html=True)

        st.markdown("""
        <div class='v27-section'>
          <span>NETWORK INTELLIGENCE</span>
          <h3>Local interfaces and listening endpoints</h3>
          <p>These observations support protocol/service discovery. They do not establish Internet exposure, remote reachability or the full enterprise topology.</p>
        </div>
        """,unsafe_allow_html=True)
        n1,n2=st.columns([1.35,.65],gap="large")
        with n1:
            ir=pd.DataFrame(interfaces);lr=pd.DataFrame(ports)
            st.markdown("<div class='v40-table-label'><span>NETWORK ADAPTERS + IP CONFIG</span><b>Local connectivity evidence</b></div>",unsafe_allow_html=True)
            st.dataframe(ir if not ir.empty else pd.DataFrame([{"Status":"No network interface evidence returned"}]),width="stretch",hide_index=True,height=min(420,150+max(len(ir),1)*46))
            st.markdown("<div class='v40-table-label' style='margin-top:14px'><span>TCP LISTENERS</span><b>Local service endpoints</b></div>",unsafe_allow_html=True)
            st.dataframe(lr if not lr.empty else pd.DataFrame([{"Status":"No TCP listener evidence returned"}]),width="stretch",hide_index=True,height=min(420,150+max(len(lr),1)*46))
        with n2:
            st.markdown("<div class='v40-purpose-panel'><span>NEXORA USE</span><h3>Network Intelligence</h3><p><b>Question:</b> which local endpoints could correspond to protocol/service surfaces?</p><p><b>Feeds:</b> protocol context and candidate service correlation.</p><p><b>Not claimed:</b> local listener evidence does not prove Internet exposure, remote reachability or TLS usage.</p><strong>CURRENT ROLE</strong><small>Observed network context · candidate protocol evidence</small></div>",unsafe_allow_html=True)
        nc=pd.DataFrame(ev.get("network_config_records") or [])
        if not nc.empty:
            st.markdown("""
            <div class='v19-insight-panel' style='margin-top:18px'>
              <span>NETWORK CONTEXT</span>
              <h3>Gateway + DNS context</h3>
              <p>Used only to describe the host's local connectivity context. NEXORA does not interpret these values as an Internet-exposure verdict.</p>
            </div>
            """,unsafe_allow_html=True)
            st.dataframe(nc,width="stretch",hide_index=True,height=min(300,130+max(len(nc),1)*44))

        st.markdown("""
        <div class='v27-section'>
          <span>CRYPTOGRAPHIC DISCOVERY</span>
          <h3>Certificates and implementation surfaces</h3>
          <p>This is the part of host evidence most directly connected to NEXORA's crypto-discovery objective.</p>
        </div>
        """,unsafe_allow_html=True)
        c1,c2=st.columns([1.35,.65],gap="large")
        with c1:
            cr=pd.DataFrame(certs);ci=pd.DataFrame(crypto);cp=pd.DataFrame(pycrypto)
            st.markdown("<div class='v40-table-label'><span>LOCAL CERTIFICATE METADATA</span><b>Direct cryptographic artifact evidence</b></div>",unsafe_allow_html=True)
            st.dataframe(cr if not cr.empty else pd.DataFrame([{"Status":"No LocalMachine certificate evidence returned"}]),width="stretch",hide_index=True,height=430)
            if not ci.empty:
                st.markdown("<div class='v40-table-label' style='margin-top:14px'><span>NATIVE CRYPTO IMPLEMENTATIONS</span><b>Discoverable tooling</b></div>",unsafe_allow_html=True);st.dataframe(ci,width="stretch",hide_index=True)
            if not cp.empty:
                st.markdown("<div class='v40-table-label' style='margin-top:14px'><span>PYTHON CRYPTO PACKAGES</span><b>NEXORA runtime implementation surface</b></div>",unsafe_allow_html=True);st.dataframe(cp,width="stretch",hide_index=True)
            if ci.empty and cp.empty: st.info("No supported cryptographic implementation metadata was returned by the collector.")
        with c2:
            st.markdown("<div class='v40-purpose-panel'><span>NEXORA USE</span><h3>Cryptographic Discovery</h3><p><b>Question:</b> which cryptographic artifacts and implementation surfaces are directly observable?</p><p><b>Feeds:</b> certificate inventory and candidate crypto-implementation investigation.</p><p><b>Not claimed:</b> implementation presence does not prove application usage.</p><strong>CURRENT ROLE</strong><small>Certificates = direct crypto evidence candidate · tooling/packages = presence evidence</small></div>",unsafe_allow_html=True)

        profile=pd.DataFrame([
            ["Hostname",ev.get("hostname")],
            ["Operating system",ev.get("os")],
            ["OS version/build",ev.get("os_version")],
            ["Architecture",ev.get("architecture")],
            ["Manufacturer",ev.get("system_manufacturer")],
            ["Model",ev.get("system_model")],
            ["Domain",ev.get("domain")],
            ["Python",ev.get("python")],
            ["Python executable",ev.get("python_executable")],
            ["OpenSSL runtime",getattr(ssl,"OPENSSL_VERSION","N/A")],
            ["Default gateways",", ".join(ev.get("default_gateways") or []) or "Not reported"],
            ["DNS servers",", ".join(ev.get("dns_servers") or []) or "Not reported"],
        ],columns=["Observed field","Value"])
        with st.expander("Host execution context · raw observed fields",expanded=False):
            st.caption("This context supports the OS-intelligence layer. It is not used as an AI/CMIS feature unless explicitly mapped in a later NEXORA version.")
            st.dataframe(profile,width="stretch",hide_index=True)

        if ev.get("collection_warnings"):
            st.markdown(
                "<div class='v28-bottom-line'><span>COLLECTION LIMITATIONS</span>"
                "<b>Only evidence actually returned by the host APIs is shown.</b>"
                "<p style='margin:5px 0 0;color:#9eb1c0;font-size:.84rem;line-height:1.6'>"+
                html.escape(" · ".join(ev["collection_warnings"][:8]))+
                "</p></div>",unsafe_allow_html=True)

        with st.expander("Raw collector payload — technical evidence only",expanded=False):
            st.json({
                k:v for k,v in ev.items()
                if k not in {"process_sample","interface_records","listening_records",
                             "service_records","certificate_records"}
            })
    if st.button("Continue to dependency tracing  →",type="primary",key="v21_discovery_next",width="stretch"):
        carry=st.session_state.get("discovery_asset") or st.session_state.get("trace_asset")
        if carry in df.id.tolist():
            st.session_state.trace_asset=carry
            go_stage("ACDKG")
        else:
            st.warning("Select a cryptographic asset above before continuing to dependency tracing.")


# ============================================================
# 03 TRACE / ACDKG
# ============================================================
elif st.session_state.stage=="ACDKG":
    selected=st.session_state.get("trace_asset")
    if selected not in df.id.tolist():
        render_page_intro("03","TRACE","Choose an asset before tracing the dependency","Trace begins only after Discovery has produced an explicit user-selected investigation target.")
        st.markdown("<div class='v31-case-seed'><div class='label'>NO TARGET YET</div><h3>Nothing is being traced.</h3><p>Return to Discovery, select a cryptographic asset, and then NEXORA will carry that selection into the ACDKG analysis.</p></div>",unsafe_allow_html=True)
        if st.button("← Return to Discovery",type="primary",key="v31_trace_back",width="stretch"): go_stage("DISCOVERY")
        render_footer();st.markdown("</div>",unsafe_allow_html=True);st.stop()

    row=df.loc[df.id==selected].iloc[0]
    depths=dependency_depths(selected)
    owners=direct_owner(selected)
    affected=impacted_components(selected)
    technical=technical_dependencies(selected)
    paths=asset_paths(selected)
    path_map=trace_path_map(selected)
    max_depth=max(depths.values(),default=0)
    transitive=max(len(depths)-len(owners),0)
    relation_types=sorted(set(G.edges[a,b].get("relation") for a,b in zip([],[])))

    render_page_intro("03","TRACE","Follow the dependency","NEXORA separates the cryptographic asset from its operational blast radius: dependency edges determine impact depth; protocol, library and algorithm links provide technical context.")
    v19_focus_asset(row)

    # The opening finding is deliberately evidence-shaped rather than a generic graph description.
    st.markdown(f"""<div class='v35-trace-answer'>
      <div><span>TRACE ANSWER</span><h3>If <b>{html.escape(str(row['name']))}</b> changes, the modeled impact reaches <b>{len(affected)} component(s)</b> through <b>{max_depth} dependency level(s)</b>.</h3></div>
      <div><small>Depth 0 = direct cryptographic owner · higher depth = transitive dependent. Technical context is shown separately and is not counted as blast radius.</small></div>
    </div>""",unsafe_allow_html=True)

    # Compact evidence counters: the first thing an engineer should be able to read without studying the graph.
    st.markdown("<div class='v35-trace-kpis'>"+
        trace_summary_card("DIRECT OWNER",len(owners),"components directly protecting the asset")+
        trace_summary_card("TRANSITIVE DEPENDENTS",transitive,"components reached through DEPENDS ON")+
        trace_summary_card("MAX DEPTH",max_depth,"furthest modeled dependency level")+
        trace_summary_card("TECHNICAL LINKS",len(technical),"protocol / library / service context")+
        trace_summary_card("PATHS",len(paths),"modeled consequence paths exposed")+
        "</div>",unsafe_allow_html=True)

    c1,c2=st.columns([1.62,.78],gap="large")
    with c1:
        st.markdown("<div class='v19-graph-shell'><div class='v19-graph-head'><span>ACDKG · DEPENDENCY BLAST RADIUS</span><b>Dependency layers are explicit</b></div>",unsafe_allow_html=True)
        st.plotly_chart(trace_graph_figure(selected),width="stretch",config={"displayModeBar":False})
        st.markdown("</div>",unsafe_allow_html=True)
    with c2:
        st.markdown(f"""<div class='v35-trace-readout'>
          <span class='eyebrow'>ASSET RECORD</span>
          <h3>{html.escape(str(row['name']))}</h3>
          <div class='v35-trace-line'><b>Current</b><span>{html.escape(str(row.algorithm))}</span></div>
          <div class='v35-trace-line'><b>Role</b><span>{html.escape(str(row.crypto_role))}</span></div>
          <div class='v35-trace-line'><b>Protocol</b><span>{html.escape(str(row.protocol))}</span></div>
          <div class='v35-trace-line'><b>Owner</b><span>{html.escape(str(row.owner))}</span></div>
          <div class='v35-trace-line'><b>PQC direction</b><span>{html.escape(str(row['Suggested PQC']))}</span></div>
          <div class='v35-trace-line'><b>Standard</b><span>{html.escape(str(PQC_STANDARD.get(row['Suggested PQC'],'Role-compatible direction')))}</span></div>
          <div class='v35-trace-context'><span>TECHNICAL CONTEXT</span><b>{html.escape(', '.join(f'{target} · {trace_relation_label(rel)}' for target,rel in technical) if technical else 'No direct protocol/library/service link recorded')}</b><small>These links explain the implementation context around the owner; they are not counted as dependency depth.</small></div>
        </div>""",unsafe_allow_html=True)

    # Exact modeled path: a professional trace should expose the evidence behind the picture.
    first_path=" → ".join(paths[0]) if paths else f"{row['name']} → {row.owner}"
    st.markdown(f"<div class='v35-primary-path'><span>PRIMARY MODELED CONSEQUENCE PATH</span><b>{html.escape(first_path)}</b><small>The path is derived from the ACDKG relationship data, not manually typed into the interface.</small></div>",unsafe_allow_html=True)

    st.markdown("<div class='v35-trace-section'><div><span>DEPENDENCY LEDGER</span><h3>Which component is affected, at what depth, and through which path?</h3><p>This table is the audit surface behind the graph. It distinguishes direct ownership from transitive dependency.</p></div></div>",unsafe_allow_html=True)
    ledger=trace_evidence_rows(selected)
    if not ledger.empty:
        st.dataframe(ledger[["Component","Layer","Depth","Type","Path","Relationships"]],width="stretch",hide_index=True,height=min(420,110+42*len(ledger)))
    else:
        st.info("No dependency relationships were found for the selected asset.")

    # Relationship semantics: useful for viva and for a professional reviewer checking what the graph means.
    rel_counts=Counter()
    for path in path_map.values():
        for a,b in zip(path,path[1:]):
            rel_counts[G.edges[a,b].get("relation","unknown")]+=1
    st.markdown("<div class='v35-trace-section'><div><span>RELATIONSHIP SEMANTICS</span><h3>What each edge means in NEXORA</h3><p>The graph is only useful if the relationship semantics are explicit.</p></div></div>",unsafe_allow_html=True)
    sem_rows=[]
    for rel,count in rel_counts.most_common():
        sem_rows.append({"Relationship":trace_relation_label(rel),"Observed in trace":count,
                         "Meaning":{
                             "protected_by":"The component directly owns/protects the selected cryptographic asset.",
                             "depends_on":"A component requires another modeled component to operate; this relationship contributes to dependency depth.",
                         }.get(rel,"Technical relationship shown as context; it does not contribute to dependency depth."),
                         "Impact counted?":"YES" if rel=="depends_on" else ("ANCHOR" if rel=="protected_by" else "CONTEXT")})
    if sem_rows:
        st.dataframe(pd.DataFrame(sem_rows),width="stretch",hide_index=True,height=min(250,70+45*len(sem_rows)))

    with st.expander("Open complete ACDKG",expanded=False):
        st.caption("Complete case graph. The focused trace above is the evidence view used by NEXORA's later assessment and planning stages.")
        st.plotly_chart(graph_figure(selected,full=True),width="stretch",config={"displayModeBar":False})

    st.markdown("<div class='v35-trace-handoff'><div><span>TRACE → ASSESS</span><b>Evidence is now established.</b><small>Assessment can use affected components, dependency depth, technical relationships and cryptographic context without rebuilding the trace.</small></div><div><span>NEXT QUESTION</span><b>Why does this dependency matter?</b><small>Assess combines this graph evidence with the NEXORA risk metric and controlled AI inference.</small></div></div>",unsafe_allow_html=True)
    if st.button("Assess this dependency  →",type="primary",key="v35_trace_next",width="stretch"):go_stage("RISK")

# ============================================================
# 04 ASSESS / RISK
# ============================================================
elif st.session_state.stage=="RISK":
    selected=st.session_state.get("trace_asset")
    if selected not in df.id.tolist():
        render_page_intro("04","ASSESS","Choose an asset before assessing impact","Assessment is derived from the dependency evidence of a user-selected asset.")
        st.markdown("<div class='v31-case-seed'><div class='label'>ASSESSMENT WAITING</div><h3>No asset has been selected yet.</h3><p>Use Discovery to select the asset whose migration consequence you want NEXORA to assess.</p></div>",unsafe_allow_html=True)
        if st.button("← Return to Discovery",type="primary",key="v31_risk_back",width="stretch"): go_stage("DISCOVERY")
        render_footer();st.markdown("</div>",unsafe_allow_html=True);st.stop()
    row=df.loc[df.id==selected].iloc[0]
    f=feature_row(row).iloc[0];affected=len(impacted_components(selected));depth=max(dependency_depths(selected).values(),default=0)
    pred=str(row["ML Effort"]);conf=float(row["ML Confidence"]);parts,raw_cmis,final_cmis,formula=v28_cmis_formula(row)
    render_page_intro("04","ASSESS","Turn dependency evidence into migration-impact evidence","This is the decision engine: NEXORA calculates a transparent project-specific risk metric, runs a controlled ML inference and turns both into planning evidence.")
    v19_focus_asset(row)
    v19_finding("ASSESSMENT ANSWER",f"{html.escape(str(row['name']))} has {html.escape(str(row['Risk']).lower())} modeled exposure because cryptographic vulnerability, infrastructure criticality, exposure, complexity and dependency impact combine into the current evidence.")
    st.markdown(f"""<div class='v28-processing-trace'>
      <div class='v28-trace-head'><span>ASSESSMENT PIPELINE</span><b>NEXORA is not showing a naked score — this is the calculation path behind the selected asset.</b></div>
      <div class='v28-trace-row'><div class='v28-trace-num'>01</div><div><span>GRAPH EVIDENCE</span><b>{affected} affected component(s) · dependency depth {depth}</b><small>ACDKG traversal supplies the dependency-impact input.</small></div></div>
      <div class='v28-trace-row'><div class='v28-trace-num'>02</div><div><span>CMIS ENGINE</span><b>{final_cmis}/100 · {html.escape(str(row['Risk']))}</b><small>Weighted calculation shown below; the score is project-specific, not a NIST score.</small></div></div>
      <div class='v28-trace-row'><div class='v28-trace-num'>03</div><div><span>AI INFERENCE</span><b>{html.escape(pred)} migration-effort class · {conf:.1f}% top-class probability</b><small>The Random Forest receives the selected asset's derived infrastructure features and returns a class plus class probabilities.</small></div></div>
      <div class='v28-trace-row'><div class='v28-trace-num'>04</div><div><span>PLANNING HAND-OFF</span><b>Evidence → preparation gates → sequence → simulation</b><small>The result becomes an input to the next stage; it is not a production command.</small></div></div>
    </div>""",unsafe_allow_html=True)

    k1,k2,k3,k4,k5=st.columns(5,gap="medium")
    for col,(lab,val,sub) in zip([k1,k2,k3,k4,k5],[("CMIS",f"{final_cmis}/100","NEXORA project metric"),("RISK",str(row.Risk),"modeled exposure band"),("IMPACT",str(affected),"affected components"),("DEPTH",str(depth),"maximum dependency depth"),("AI EFFORT",pred,"controlled ML class")]):
        with col: st.markdown(f"<div class='v27-assess-kpi'><span>{lab}</span><b>{html.escape(val)}</b><small>{html.escape(sub)}</small></div>",unsafe_allow_html=True)

    st.markdown("<div class='v28-formula-card'><div class='v18-eyebrow'>CMIS · NEXORA PROJECT METRIC</div><h2 style='margin:5px 0 0;font-size:1.55rem'>Why is the selected asset at this score?</h2><p class='v28-formula-note'>CMIS combines five modeled evidence dimensions. Each observed value is multiplied by the project-defined weight, then the result is capped at 100.</p><div class='v28-formula'>CMIS = (V × 8) + (C × 6) + (E × 5) + (M × 4) + (D × 3)</div><p class='v28-formula-note'><b>V</b> = cryptographic vulnerability · <b>C</b> = criticality · <b>E</b> = exposure · <b>M</b> = migration complexity · <b>D</b> = dependency impact factor (capped at 5).</p></div>",unsafe_allow_html=True)
    st.markdown(f"""<div class='v28-score-hero'><div><div class='v18-eyebrow'>SELECTED ASSET RESULT</div><div class='score'>{final_cmis}<small> / 100 CMIS</small></div><p>Raw weighted total = {raw_cmis}. The displayed value is capped at 100.</p></div><div><div class='risk'>{html.escape(str(row['Risk']))}</div><p>Risk band is determined from the NEXORA project thresholds.</p></div></div><div class='v28-band-row'><div class='v28-band {'active' if final_cmis<=30 else ''}'>0–30 · LOW</div><div class='v28-band {'active' if 31<=final_cmis<=60 else ''}'>31–60 · MODERATE</div><div class='v28-band {'active' if 61<=final_cmis<=80 else ''}'>61–80 · HIGH</div><div class='v28-band {'active' if final_cmis>=81 else ''}>81–100 · CRITICAL</div></div>""",unsafe_allow_html=True)

    c1,c2=st.columns([1.05,.95],gap="large")
    with c1:
        st.markdown("<div class='v27-chart-card'><span>CMIS BREAKDOWN</span><h3>How each factor contributes</h3><p>The table makes the score reproducible instead of leaving “100” unexplained.</p></div>",unsafe_allow_html=True)
        cm=pd.DataFrame([{"Factor":n,"Observed":v,"Weight":w,"Contribution":c} for n,v,w,c in parts]);st.dataframe(cm,width="stretch",hide_index=True,height=300)
    with c2:
        st.markdown("<div class='v27-chart-card'><span>RISK DIMENSIONS</span><h3>Shape of the selected evidence</h3><p>Each dimension is scored from 1–5 inside the controlled case model.</p></div>",unsafe_allow_html=True);st.plotly_chart(assessment_radar_figure(row),width="stretch",config={"displayModeBar":False})

    st.markdown(f"<div class='v27-chart-card'><span>CASE LANDSCAPE</span><h3>Where this asset sits relative to the other case assets</h3><p>X-axis = affected modeled components · Y-axis = CMIS. The selected asset is marked with a star.</p><div style='display:flex;gap:22px;flex-wrap:wrap;margin-top:10px;color:#9eb1c0;font-size:.78rem'><span><b style='color:#e8f3f8'>SELECTED</b> · {html.escape(str(row['name']))}</span><span>CMIS <b style='color:#e8f3f8'>{final_cmis}</b></span><span>Impact <b style='color:#e8f3f8'>{affected}</b> components</span><span>Depth <b style='color:#e8f3f8'>{depth}</b></span></div></div>",unsafe_allow_html=True);st.plotly_chart(assessment_landscape_figure(selected),width="stretch",config={"displayModeBar":False})

    # Real model input vector + output probabilities.
    c1,c2=st.columns([1.0,1.0],gap="large")
    with c1:
        st.markdown("<div class='v27-chart-card'><span>AI INPUT VECTOR</span><h3>What the Random Forest actually receives</h3><p>These are derived features for the selected asset — not a fabricated text explanation.</p><div style='display:flex;gap:7px;flex-wrap:wrap;margin-top:10px'><span style='padding:5px 9px;border:1px solid #29485e;border-radius:999px;color:#9ed1f2;font-size:.68rem;font-weight:800;letter-spacing:.06em'>CASE · controlled inputs</span><span style='padding:5px 9px;border:1px solid #29485e;border-radius:999px;color:#9ed1f2;font-size:.68rem;font-weight:800;letter-spacing:.06em'>ACDKG · graph-derived</span><span style='padding:5px 9px;border:1px solid #29485e;border-radius:999px;color:#9ed1f2;font-size:.68rem;font-weight:800;letter-spacing:.06em'>CRYPTO · asset context</span></div></div>",unsafe_allow_html=True)
        origin_map={"criticality":"CASE","exposure":"CASE","complexity":"CASE","dependency_depth":"ACDKG","operational_dependents":"ACDKG","technical_dependencies":"ACDKG","vulnerability":"CRYPTO"}
        vector=pd.DataFrame([{"Feature":k.replace('_',' ').title(),"Value":float(f[k]),"Origin":origin_map.get(k,"DERIVED")} for k in ML_FEATURES]);st.dataframe(vector,width="stretch",hide_index=True,height=315)
        st.markdown(f"<div class='v28-ai-output'>Inference result → {html.escape(pred)} effort class · top-class probability {conf:.1f}%</div>",unsafe_allow_html=True)
    with c2:
        st.markdown("<div class='v27-chart-card'><span>AI OUTPUT DISTRIBUTION</span><h3>How the classifier arrived at its class</h3><p>These are the Random Forest class probabilities for this synthetic scenario.</p></div>",unsafe_allow_html=True);st.plotly_chart(v28_probability_figure(row),width="stretch",config={"displayModeBar":False})

    st.markdown("<div class='v27-chart-card'><span>MODEL LEARNED SIGNALS</span><h3>Which features influence the trained classifier?</h3><p>Feature importance describes the model's learned split usage on the controlled synthetic training data; it is not causal evidence from a real enterprise.</p></div>",unsafe_allow_html=True);st.plotly_chart(assessment_feature_figure(),width="stretch",config={"displayModeBar":False})
    live_ai_whatif(row,f)
    st.markdown(f"<div class='v32-handoff'><div><span>ASSESSMENT HAND-OFF</span><b>{html.escape(str(row['name']))} → planning</b><small>{affected} affected component(s) · depth {depth} · CMIS {final_cmis}/100 · RF class {html.escape(pred)}</small></div><div><b>Planning receives</b><small>Dependency impact · CMIS/risk evidence · role-aware PQC direction · AI effort signal. The next stage turns these findings into preparation gates and migration sequence.</small></div></div>",unsafe_allow_html=True)
    if st.button("Generate migration plan  →",type="primary",key="v28_risk_next",width="stretch"): go_stage("PLAN")

# ============================================================
# 05 PLAN
# ============================================================
elif st.session_state.stage=="PLAN":
    selected=st.session_state.get("trace_asset")
    if selected not in df.id.tolist():
        render_page_intro("05","PLAN","Choose an asset before planning migration","Planning requires a concrete dependency target selected through Discovery.")
        st.markdown("<div class='v31-case-seed'><div class='label'>PLAN WAITING</div><h3>No migration target has been selected yet.</h3><p>Return to Discovery and choose the cryptographic asset whose dependency-aware preparation should be generated.</p></div>",unsafe_allow_html=True)
        if st.button("← Return to Discovery",type="primary",key="v31_plan_back",width="stretch"): go_stage("DISCOVERY")
        render_footer();st.markdown("</div>",unsafe_allow_html=True);st.stop()

    row=df.loc[df.id==selected].iloc[0]
    gates=prepare_asset_decision(row)
    plan=build_plan()
    depths=dependency_depths(selected)
    affected=len(impacted_components(selected))
    depth=max(depths.values(),default=0)
    owners=direct_owner(selected)
    tech=technical_dependencies(selected)
    protocols=[n for n,r in tech if r=="uses_protocol"]
    libs=[n for n,r in tech if r=="uses_library"]
    dependents=max(len(depths)-len(owners),0)
    strategy=strategy_for(row)
    target=str(row["Suggested PQC"])

    render_page_intro("05","PLAN","Turn assessment into a dependency-aware migration sequence","NEXORA converts TRACE evidence and ASSESS signals into preparation gates, engineering workstreams and a controlled change sequence.")
    v19_focus_asset(row)

    # --------------------------------------------------------
    # 01 · SINGLE PLANNING ANSWER
    # --------------------------------------------------------
    v19_finding("PLANNING ANSWER",f"NEXORA does not plan the cryptographic replacement in isolation. It prepares the dependency path around {html.escape(str(row['name']))}: {affected} modeled component(s), dependency depth {depth}, {dependents} downstream dependent(s), and {len(tech)} direct technical relationship(s).")

    st.markdown(f"""
    <div class='v33-plan-command'>
      <div class='v33-plan-command-main'>
        <span>RECOMMENDED STRATEGY · CONTROLLED PROTOTYPE</span>
        <h2>{html.escape(strategy)}</h2>
        <p><b>{html.escape(str(row.id))} · {html.escape(str(row.algorithm))}</b> → <b>{html.escape(target)}</b> · {html.escape(str(row.crypto_role))} · {html.escape(str(row.protocol))}</p>
      </div>
      <div class='v33-plan-command-stats'>
        <div><span>AFFECTED</span><b>{affected}</b><small>modeled components</small></div>
        <div><span>DEPTH</span><b>{depth}</b><small>dependency levels</small></div>
        <div><span>DEPENDENTS</span><b>{dependents}</b><small>downstream</small></div>
        <div><span>AI EFFORT</span><b>{html.escape(str(row['ML Effort']))}</b><small>assessment signal</small></div>
      </div>
    </div>
    """,unsafe_allow_html=True)

    # --------------------------------------------------------
    # 02 · MIGRATION GATES — the actual orchestration layer
    # --------------------------------------------------------
    st.markdown("<div class='v33-section-head'><span>01 · MIGRATION GATES</span><h3>What must be true before the change?</h3><p>These are asset-specific preparation conditions derived from the selected dependency, protocol, library and migration context. They are planning requirements — not claims that the prototype has already executed the checks.</p></div>",unsafe_allow_html=True)

    gate_cards=[]
    gate_cards.append(("01","DEPENDENCY READY",f"{affected} affected component(s) · depth {depth}","DERIVED","ACDKG"))
    if protocols:
        gate_cards.append(("02","PROTOCOL READY",", ".join(protocols),"REQUIRED","TECHNICAL LINK"))
    if libs:
        gate_cards.append(("03","LIBRARY READY",", ".join(libs),"REQUIRED","TECHNICAL LINK"))
    if row["type"]=="Certificate" or any(n=="PKI" for n,_ in tech):
        gate_cards.append((f"{len(gate_cards)+1:02d}","TRUST / PKI READY","Certificate lifecycle + trust-chain validation","REQUIRED","PKI"))
    gate_cards.append((f"{len(gate_cards)+1:02d}","COMPATIBILITY READY","Controlled service-continuity validation","REQUIRED","NEXORA PLAN"))
    gate_cards.append((f"{len(gate_cards)+1:02d}","CHANGE READY",f"Controlled introduction of {target}","GATED","NEXORA PLAN"))
    gate_cards.append((f"{len(gate_cards)+1:02d}","POST-CHANGE VERIFIED","Revalidate services, trust and inventory","REQUIRED","NEXORA PLAN"))

    st.markdown("<div class='v33-gate-grid'>"+"".join(
        f"<div class='v33-gate-card'><div class='v33-gate-top'><span>{num}</span><em>{html.escape(status)}</em></div><b>{html.escape(title)}</b><p>{html.escape(detail)}</p><small>{html.escape(source)}</small></div>"
        for num,title,detail,status,source in gate_cards
    )+"</div>",unsafe_allow_html=True)

    # --------------------------------------------------------
    # 03 · THREE READABLE PLANNING DEPTHS — preserve existing diagrams
    # --------------------------------------------------------
    st.markdown("<div class='v33-section-head'><span>02 · PLANNING DEPTH</span><h3>Same decision, three engineering views.</h3><p>Level 0 is the decision view. Level 1 exposes the workstreams that must meet. Level 2 gives the technical validation surface.</p></div>",unsafe_allow_html=True)

    st.markdown("<div class='v32-plan-level'><span>LEVEL 0 · NON-TECHNICAL DECISION</span><h3>Understand the order.</h3><p>Prepare → validate → controlled change → verify.</p></div>",unsafe_allow_html=True)
    st.plotly_chart(plan_level_figure(0,row),width='stretch',config={'displayModeBar':False})

    st.markdown("<div class='v32-plan-level'><span>LEVEL 1 · ENGINEERING PLAN</span><h3>Which workstreams must meet?</h3><p>Asset → PKI / replacement → protocol → owner/service → controlled validation → go / hold.</p></div>",unsafe_allow_html=True)
    st.plotly_chart(plan_level_figure(1,row),width='stretch',config={'displayModeBar':False})

    st.markdown(f"<div class='v32-plan-level'><span>LEVEL 2 · TECHNICAL SPECIFICATION</span><h3>What exactly must be checked?</h3><p>{html.escape(str(row.id))} · {html.escape(str(row.algorithm))} → {html.escape(target)} · {html.escape(str(row.protocol))} · owner {html.escape(str(row.owner))}. The technical view expands implementation, trust and continuity checkpoints.</p></div>",unsafe_allow_html=True)
    st.plotly_chart(plan_level_figure(2,row),width='stretch',config={'displayModeBar':False})

    # --------------------------------------------------------
    # 04 · EVIDENCE → ACTION MAPPING
    # --------------------------------------------------------
    st.markdown("<div class='v33-section-head'><span>03 · WHY THIS ORDER</span><h3>Evidence is mapped to an action — not just displayed.</h3><p>This is the orchestration link between TRACE / ASSESS and the migration sequence.</p></div>",unsafe_allow_html=True)
    mapping=[
        ("ACDKG",f"{affected} affected component(s), depth {depth}","Dependency validation is placed before the cryptographic change."),
        ("CRYPTO",f"{row['crypto_role']} · {row['algorithm']} → {target}","The replacement direction is role-aware rather than algorithm-name substitution."),
        ("TECHNICAL",f"{len(protocols)} protocol link(s) · {len(libs)} library link(s)","Compatibility checks are introduced where the graph has technical relationships."),
        ("ASSESS",f"{row['Risk']} risk · {row['ML Effort']} modeled effort",f"The assessment signal supports a {strategy.lower()} posture; it does not execute the migration."),
    ]
    st.markdown("<div class='v33-evidence-map'>"+"".join(f"<div><span>{html.escape(a)}</span><b>{html.escape(b)}</b><p>{html.escape(c)}</p></div>" for a,b,c in mapping)+"</div>",unsafe_allow_html=True)

    # Existing asset-specific gates retained as technical evidence.
    with st.expander("Technical evidence · asset-specific preparation details",expanded=False):
        st.markdown("<div class='v19-table-caption'><div><h3>Concrete preparation requirements</h3><p>Generated from the selected asset's owner, role, protocol, library relationships and dependency evidence.</p></div></div>",unsafe_allow_html=True)
        st.markdown("<div class='v19-gates'>"+"".join(f"<div class='v19-gate'><span>{html.escape(phase)}</span><b>{html.escape(text)}</b></div>" for phase,text in gates)+"</div>",unsafe_allow_html=True)

    # --------------------------------------------------------
    # 05 · CASE ORDERING — secondary, never the main decision
    # --------------------------------------------------------
    with st.expander("Case-level migration ordering",expanded=False):
        planner=plan[["order","id","name","algorithm","target","risk","cmis","affected","effort","signal"]].copy()
        planner.columns=["Order","Asset","Name","Current","PQC target","Risk","CMIS","Affected","AI effort","Planning signal"]
        st.dataframe(planner,width="stretch",hide_index=True)
        st.caption("Planning signal is an internal prototype ordering value. The user-facing decision above is explained through dependency evidence, assessment signals and preparation gates — not the number alone.")

    # --------------------------------------------------------
    # 06 · PLAN → SIMULATION hand-off
    # --------------------------------------------------------
    st.markdown(f"""
    <div class='v33-plan-handoff'>
      <div><span>PLAN → SIMULATE</span><b>{html.escape(str(row['name']))}</b><small>Sequence: dependency validation → compatibility preparation → controlled {html.escape(target)} change → post-change verification.</small></div>
      <div><span>SIMULATION INPUT</span><b>{affected} affected · depth {depth}</b><small>The next stage tests the consequence model; it does not execute a real cryptographic change.</small></div>
    </div>
    """,unsafe_allow_html=True)
    if st.button("Run consequence simulation  →",type="primary",key="v28_plan_next",width="stretch"):
        st.session_state.simulation_asset=selected;st.session_state.simulation_result=None;go_stage("SIMULATE")



# ============================================================
# 06 SIMULATE — SIMULATION V2 · STATE-TRANSITION DECISION SURFACE
# ============================================================
elif st.session_state.stage=="SIMULATE":
    selected=st.session_state.get("simulation_asset") or st.session_state.get("trace_asset")
    render_page_intro("06","SIMULATE","Model the consequence before the change","A focused what-if environment: trace the dependency surface, prepare validation gates, model the cryptographic transition, then reach a decision gate.")
    if selected not in df.id.tolist():
        st.markdown("<div class='v31-case-seed'><div class='label'>SIMULATION WAITING</div><h3>Select an asset before proposing a change.</h3><p>Discovery determines the asset. Simulation requires a role-compatible PQC target.</p></div>",unsafe_allow_html=True)
        if st.button("← Return to Discovery",type="primary",key="v42_sim_back",width="stretch"): go_stage("DISCOVERY")
        st.stop()
    st.session_state.simulation_asset=selected
    row=df.loc[df.id==selected].iloc[0]
    options=PQC_OPTIONS.get(row.crypto_role,[])
    target=st.session_state.get("pqc_target")
    if target not in options: target=None
    if target is None:
        st.markdown("<div class='v31-case-seed'><div class='label'>TARGET REQUIRED</div><h3>No PQC target has been selected.</h3><p>Choose a role-compatible PQC target in the Investigation Controls above before starting the simulation.</p></div>",unsafe_allow_html=True)
        st.stop()

    result=st.session_state.get("simulation_result")
    if not result:
        st.markdown(f"""
        <div class='v42-sim'>
          <div class='v42-head'>
            <div class='v42-kicker'>SIMULATION LAB · CONTROLLED WHAT-IF MODEL</div>
            <h2>What happens if this cryptographic dependency changes?</h2>
            <p>NEXORA keeps the modeled infrastructure fixed and changes the migration sequence. The simulation exposes the dependency surface and validation gates before a real deployment decision.</p>
            <div class='v42-transition'><span class='v42-asset current'>{html.escape(str(row.id))} · {html.escape(str(row.algorithm))}</span><span class='v42-arrow'>→</span><span class='v42-asset'>{html.escape(str(target))}</span><span class='v42-meta'>{html.escape(str(row.crypto_role))} · {html.escape(str(row.protocol))} · {html.escape(str(PQC_STANDARD.get(target,'NIST PQC standard')))}</span></div>
          </div>
          <div class='v42-contract'><b>Simulation boundary:</b> controlled modeled state transitions only. No OS, certificate, key, protocol or production-service configuration is modified.</div>
          <div class='v42-strategy'><div class='v42-strategy-label'>THE EXPERIMENT</div><div class='v42-strategy-grid'>
            <div class='v42-strategy-card active'><span class='tag'>PATH A</span><b>NEXORA-GUIDED</b><small>Trace → prepare → change → validate</small></div>
            <div class='v42-strategy-card'><span class='tag'>PATH B</span><b>IMMEDIATE CHANGE</b><small>Change first → discover impact → validate</small></div>
          </div></div>
        </div>
        """,unsafe_allow_html=True)
        if st.button("Initialize simulation  →",type="primary",key="v42_init_sim",width="stretch"):
            st.session_state.simulation_result=simulate(row,target)
            st.session_state.simulation_step=0
            st.session_state.simulation_mode="guided"
            st.rerun()
        st.stop()

    base_steps=simulation_v2_steps()
    step=int(st.session_state.get("simulation_step",0)); step=max(0,min(step,len(base_steps)-1)); st.session_state.simulation_step=step
    mode=st.session_state.get("simulation_mode","guided")
    if mode not in {"guided","immediate"}: mode="guided"

    # Compact strategy selector: same case, same target, different sequence.
    s1,s2=st.columns(2,gap="small")
    with s1:
        if st.button("NEXORA-GUIDED · prepare before change",key="v42_mode_guided",type="primary" if mode=="guided" else "secondary",width="stretch"):
            st.session_state.simulation_mode="guided"; st.session_state.simulation_step=0; st.rerun()
    with s2:
        if st.button("DIRECT MIGRATION · change before preparation",key="v42_mode_immediate",type="primary" if mode=="immediate" else "secondary",width="stretch"):
            st.session_state.simulation_mode="immediate"; st.session_state.simulation_step=0; st.rerun()

    title,text,affected,depth,checks,issues,why=simulation_v2_content(row,target,result,step,mode)
    guided=(mode=="guided")
    if guided:
        step_names=["BASELINE","IMPACT","PREPARE","CHANGE","VALIDATE","DECISION"]
        step_sub=["Current state","Dependency surface","Validation gates","PQC transition","Post-change checks","Migration gate"]
    else:
        step_names=["BASELINE","CHANGE","IMPACT","REMEDIATE","VALIDATE","DECISION"]
        step_sub=["Current state","Change first","Discover after change","Review / remediation","Post-change checks","Migration gate"]

    st.markdown(f"""
    <div class='v42-sim'>
      <div class='v42-head'>
        <div class='v42-kicker'>SIMULATION LAB · STEP {step+1:02d}/06 · {html.escape('NEXORA-GUIDED' if guided else 'DIRECT MIGRATION')}</div>
        <h2>{html.escape(title)}</h2>
        <p>Same modeled case and cryptographic target; this step shows what the selected migration sequence does next.</p>
        <div class='v42-transition'><span class='v42-asset current'>{html.escape(str(row.id))} · {html.escape(str(row.algorithm))}</span><span class='v42-arrow'>→</span><span class='v42-asset'>{html.escape(str(target))}</span><span class='v42-meta'>{html.escape(str(row.crypto_role))} · {html.escape(str(row.protocol))} · {html.escape(str(PQC_STANDARD.get(target,'NIST PQC standard')))}</span></div>
      </div>
      <div class='v42-steps'>{''.join(f"<div class='v42-step {'active' if i==step else 'done' if i<step else ''}'><span class='num'>0{i+1}</span><b>{html.escape(step_names[i])}</b><small>{html.escape(step_sub[i])}</small></div>" for i in range(6))}</div>
    </div>
    """,unsafe_allow_html=True)

    # Layman-readable causal explanation. The technical panels below remain the evidence layer.
    st.markdown(f"""
    <div class='v42-plain {'warn' if not guided and step>=1 else ''}'>
      <div class='icon'>{'!' if not guided and step>=1 else 'i'}</div>
      <div><b>WHAT JUST HAPPENED</b><p>{html.escape(text)}</p></div>
    </div>
    """,unsafe_allow_html=True)

    # Four migration gates make the sequence difference visible without requiring graph literacy.
    if guided:
        gate_state=[
            ("DEPENDENCY","ready","✓","Identified" if step>=1 else "Baseline"),
            ("COMPATIBILITY","ready" if step>=2 else "pending","✓" if step>=2 else "○","Prepared" if step>=2 else "Pending"),
            ("CHANGE","applied" if step>=3 else "pending","→" if step>=3 else "○","Modeled" if step>=3 else "Pending"),
            ("VERIFY","ready" if step>=4 else "pending","✓" if step>=4 else "○","Checked" if step>=4 else "Pending"),
        ]
        gate_summary="Preparation precedes the modeled change."
    else:
        gate_state=[
            ("DEPENDENCY","warn" if step>=1 else "pending","⚠" if step>=1 else "○","Skipped" if step>=1 else "Pending"),
            ("COMPATIBILITY","warn" if step>=1 else "pending","⚠" if step>=1 else "○","Post-change review" if step>=1 else "Pending"),
            ("CHANGE","applied" if step>=1 else "pending","→" if step>=1 else "○","Applied first" if step>=1 else "Pending"),
            ("VERIFY","warn" if step>=3 else "pending","⚠" if step>=3 else "○","Required" if step>=3 else "Pending"),
        ]
        gate_summary="The change occurs before dependency and compatibility preparation."
    gate_html="".join(f"<div class='v42-gatebox {state}'><span class='state'>{icon}</span><b>{label}</b><small>{sub}</small></div>" for label,state,icon,sub in gate_state)
    st.markdown(f"<div class='v42-gatestrip'><div class='v42-gatestrip-head'><span>MIGRATION GATES</span><b>{html.escape(gate_summary)}</b></div><div class='v42-gates'>{gate_html}</div></div>",unsafe_allow_html=True)

    # Primary evidence surface: one ACDKG topology and one reasoning/validation panel.
    left,right=st.columns([1.55,.85],gap="small")
    with left:
        st.markdown(f"<div class='v42-panel'><div class='v42-panel-head'><div><span>IMPACT TOPOLOGY</span><b>{'Prepared dependency surface' if guided else 'Post-change impact surface'}</b></div><em>{'GUIDED' if guided else 'DIRECT'}</em></div><div class='v42-graph'>",unsafe_allow_html=True)
        st.plotly_chart(simulation_v2_graph(selected,step,mode,target),width="stretch",config={"displayModeBar":False},key=f"v42_graph_{step}_{mode}")
        st.markdown("</div></div>",unsafe_allow_html=True)
    with right:
        gate_lines=[]
        if guided:
            for i,c in enumerate(checks):
                state="ready" if step>=4 else ("ready" if step>=2 and i<2 else "pending")
                gate_lines.append(f"<div class='v42-gate {state}'><span class='state'>{'✓' if state=='ready' else '○'}</span><span>{html.escape(str(c))}</span></div>")
            issue_html=""
        else:
            for c in issues[:5]:
                gate_lines.append(f"<div class='v42-gate warn'><span class='state'>⚠</span><span>{html.escape(str(c))}</span></div>")
            issue_html=(f"<div class='v42-issue'><b>WHY THIS IS DIFFERENT</b><span>The same evidence is discovered after the modeled change, so these checks become post-change review/remediation work.</span></div>" if step>=2 else "")
        if not gate_lines:
            gate_lines=["<div class='v42-gate ready'><span class='state'>✓</span><span>Baseline evidence loaded</span></div>"]
        st.markdown(f"""
        <div class='v42-panel'>
          <div class='v42-panel-head'><div><span>CURRENT FINDING</span><b>{'NEXORA REASONING' if guided else 'DIRECT PATH CONSEQUENCE'}</b></div></div>
          <div class='v42-readout'>
            <div class='v42-finding-kicker'>{'NEXORA REASONING' if guided else 'DIRECT PATH CONSEQUENCE'}</div>
            <h3>{html.escape(title)}</h3>
            <p>{html.escape(text)}</p>
            <div class='v42-metrics'>
              <div class='v42-metric'><span>AFFECTED</span><b>{affected}</b></div>
              <div class='v42-metric'><span>MAX DEPTH</span><b>{depth}</b></div>
              <div class='v42-metric'><span>{'VALIDATION GATES' if guided else 'REVIEW CONDITIONS'}</span><b>{len(checks) if guided else len(issues)}</b></div>
              <div class='v42-metric'><span>PRODUCTION CHANGES</span><b>0</b></div>
            </div>
            <div class='v42-section-title'>{'REQUIRED GATES' if guided else 'ISSUES REQUIRING REVIEW'}</div>
            {''.join(gate_lines)}
            {issue_html}
          </div>
        </div>
        """,unsafe_allow_html=True)
        st.markdown(f"<div class='v42-why'><b>WHY THIS MATTERS</b><small>{html.escape(str(why))}</small></div>",unsafe_allow_html=True)

    # Explicit before/after delta.
    st.markdown(f"""
    <div class='v42-delta'>
      <div class='v42-delta-side'><div class='label'>CURRENT STATE</div><b>{html.escape(str(row.algorithm))}</b><small>{html.escape(str(row.crypto_role))} · {html.escape(str(row.protocol))}</small></div>
      <div class='v42-delta-arrow'>→</div>
      <div class='v42-delta-side'><div class='label'>PROPOSED STATE</div><b>{html.escape(str(target))}</b><small>{html.escape(str(PQC_STANDARD.get(target,'NIST PQC standard')))} · modeled target</small></div>
    </div>
    """,unsafe_allow_html=True)

    active_chain=min(step+1,5)
    if guided:
        chain_labels=[("01","CRYPTO ASSET"),("02","OWNER"),("03","DEPENDENCY"),("04","TECHNICAL"),("05","VALIDATION")]
    else:
        chain_labels=[("01","CRYPTO ASSET"),("02","CHANGE"),("03","IMPACT"),("04","REVIEW"),("05","VALIDATION")]
    chain_html="".join(f"<div class='{'active' if i<active_chain else ''}'><span>{num}</span><b>{label}</b></div>" for i,(num,label) in enumerate(chain_labels))
    st.markdown(f"<div class='v42-propagation'><h3>{'CHANGE PROPAGATION' if guided else 'POST-CHANGE PROPAGATION'}</h3><div class='v42-chain'>{chain_html}</div></div>",unsafe_allow_html=True)

    # Compact sequence comparison: this is the conceptual payoff of the simulation.
    st.markdown(f"""
    <div class='v42-sequence'><h3>SEQUENCE CONSEQUENCE</h3>
      <div class='v42-seqrow'><span>NEXORA-GUIDED</span><div><i class='current'>DISCOVER</i><span class='v42-mini-arrow'>→</span><i class='current'>PREPARE</i><span class='v42-mini-arrow'>→</span><i>CHANGE</i><span class='v42-mini-arrow'>→</span><i>VALIDATE</i></div></div>
      <div class='v42-seqrow'><span>DIRECT</span><div><i class='{'warn' if not guided else ''}'>CHANGE</i><span class='v42-mini-arrow'>→</span><i class='{'warn' if not guided else ''}'>DISCOVER IMPACT</i><span class='v42-mini-arrow'>→</span><i class='{'warn' if not guided else ''}'>REVIEW / REMEDIATE</i><span class='v42-mini-arrow'>→</span><i>VALIDATE</i></div></div>
    </div>
    """,unsafe_allow_html=True)

    # Compact technical trace. Keep it secondary to the causal story.
    if guided:
        events=[
            ("00:01","LOAD",f"{row.id} · {row.algorithm} → {target}"),
            ("00:02","TRACE",f"{affected} affected component(s), max depth {depth}"),
            ("00:03","PREP",f"{len(checks)} validation gate(s) established before change"),
            ("00:04","CHANGE",f"{row.algorithm} → {target} modeled"),
            ("00:05","VERIFY","Post-change validation remains required"),
        ][:max(1,step+1)]
    else:
        events=[
            ("00:01","LOAD",f"{row.id} · {row.algorithm} → {target}"),
            ("00:02","CHANGE",f"{row.algorithm} → {target} modeled before preparation"),
            ("00:03","IMPACT",f"{affected} affected component(s) discovered after change"),
            ("00:04","REVIEW",f"{len(issues)} post-change review condition(s) exposed"),
            ("00:05","VERIFY","Validation / remediation remains required"),
        ][:max(1,step+1)]
    event_html="".join(f"<div class='v42-log-row'><time>{html.escape(a)}</time><b>{html.escape(b)}</b><span>{html.escape(c)}</span></div>" for a,b,c in events)
    checks_preview=("".join(f"<div class='v42-gate {'warn' if not guided else 'pending'}'><span class='state'>{'⚠' if not guided else '○'}</span><span>{html.escape(str(c))}</span></div>" for c in (issues if not guided else checks)[:5]))
    if not checks_preview: checks_preview="<div class='v42-gate ready'><span class='state'>✓</span><span>Baseline evidence is available</span></div>"
    b1,b2=st.columns([1,.95],gap="small")
    with b1: st.markdown(f"<div class='v42-log'><h3>SIMULATION TRACE</h3>{event_html}</div>",unsafe_allow_html=True)
    with b2: st.markdown(f"<div class='v42-log'><h3>{'VALIDATION REQUIREMENTS' if guided else 'ISSUES REQUIRING REVIEW'}</h3>{checks_preview}</div>",unsafe_allow_html=True)

    c1,c2,c3=st.columns([1,1.2,1],gap="small")
    with c1:
        if st.button("Reset",key="v42_reset",width="stretch"): st.session_state.simulation_step=0; st.rerun()
    with c2:
        if st.button("← Previous",key="v42_prev",disabled=step==0,width="stretch"): st.session_state.simulation_step=step-1; st.rerun()
    with c3:
        if st.button("Next step →",key="v42_next",disabled=step>=5,width="stretch"): st.session_state.simulation_step=step+1; st.rerun()

    if step==5:
        if guided:
            decision_title="VALIDATION-AWARE MIGRATION GATE"
            decision_text="NEXORA has established the dependency and validation sequence before the modeled transition. The next real migration step still requires environment-specific external validation."
        else:
            decision_title="REMEDIATION-AWARE MIGRATION GATE"
            decision_text="The direct sequence introduced the modeled change before dependency preparation, leaving post-change review and potential remediation work to resolve before a real migration step."
        st.markdown(f"""
        <div class='v42-decision {'good' if guided else 'warn'}'>
          <div class='kicker'>DECISION GATE</div>
          <h2>{decision_title}</h2>
          <p>{html.escape(decision_text)}</p>
          <div class='v42-decision-grid'><div><span>AFFECTED COMPONENTS</span><b>{affected}</b></div><div><span>DEPENDENCY DEPTH</span><b>{depth}</b></div><div><span>{'VALIDATION GATES' if guided else 'REVIEW CONDITIONS'}</span><b>{len(checks) if guided else len(issues)}</b></div><div><span>PRODUCTION CHANGES</span><b>0</b></div></div>
          <div class='v42-note'>Modeled state only · the prototype does not claim production compatibility, outage, recovery success or deployment completion.</div>
        </div>
        """,unsafe_allow_html=True)

    with st.expander("Technical simulation evidence",expanded=False):
        st.json({"asset":str(row.id),"current_algorithm":str(row.algorithm),"target":str(target),"role":str(row.crypto_role),"mode":mode,"step":step,"affected_components":impacted_components(selected),"dependency_depth":depth,"checks":checks,"modeled_review_conditions":issues,"source_conflicts":result.get("conflicts",[]),"status":result.get("status")})

render_footer()
st.markdown("</div>",unsafe_allow_html=True)
