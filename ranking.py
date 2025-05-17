from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, validator
from typing import List, Optional
import pandas as pd
import numpy as np
from datetime import datetime
import logging

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 初始化 FastAPI 应用
app = FastAPI(title="Author Analysis API", version="1.0.0")

# 配置 CORS 中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 全局数据存储
dfs = {}

# 字段映射
FIELD_MAPPINGS = {
    2020: {
        'total_pubs': 'np6020',
        'cites_ns': 'nc2020 (ns)',
        'cites': 'nc2020',
        'h_index_ns': 'h20 (ns)',
        'npsfl': 'npsfl (ns)',
        'cpsf': 'cpsf (ns)',
        'nps': 'nps (ns)',
    },
    2021: {
        'total_pubs': 'np6021',
        'cites_ns': 'nc2121 (ns)',
        'cites': 'nc2121',
        'h_index_ns': 'h21 (ns)',
        'npsfl': 'npsfl (ns)',
        'cpsf': 'cpsf (ns)',
        'nps': 'nps (ns)',
    },
    2022: {
        'total_pubs': 'np6022',
        'cites_ns': 'nc2222 (ns)',
        'cites': 'nc2222',
        'h_index_ns': 'h22 (ns)',
        'npsfl': 'npsfl (ns)',
        'cpsf': 'cpsf (ns)',
        'nps': 'nps (ns)',
    },
    2023: {
        'total_pubs': 'np6023',
        'cites_ns': 'nc2323 (ns)',
        'cites': 'nc2323',
        'h_index_ns': 'h23 (ns)',
        'npsfl': 'npsfl (ns)',
        'cpsf': 'cpsf (ns)',
        'nps': 'nps (ns)',
    }
}


# 加载 Excel 数据
async def load_data():
    global dfs
    if dfs:
        logger.info("数据已加载，跳过重复加载")
        return

    years = [2020, 2021, 2022, 2023]
    for year in years:
        try:
            df = pd.read_excel(
                f"E:/SessionMaterial/Session2025Spring/MATH3710/project/dataset/Table_1_Authors_singleyr_{year}_pubs_since_1788_wopp_extracted_202408.xlsx",
                sheet_name="Data"
            )
            # 数据预处理
            df['authfull'] = df['authfull'].astype(str)
            df['cntry'] = df['cntry'].astype(str)
            df['first_name'] = df['authfull'].apply(lambda x: x.split(',')[1].strip() if ',' in x else "")
            df['last_name'] = df['authfull'].apply(lambda x: x.split(',')[0].strip() if ',' in x else "")
            df['full_name'] = df['first_name'] + " " + df['last_name']
            df['inst_name'] = df['inst_name'].fillna("Unknown").str.strip().str.lower()
            dfs[year] = df
            logger.info("loading %s data successfully", year)
        except Exception as e:
            logger.error("loading %s data failed: %s", year, str(e))
            raise


# 启动事件
@app.on_event("startup")
async def startup_event():
    logger.info("Loading data...")
    await load_data()


class SearchRequest(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    country: str | None = None


class GenerateAnalysisRequest(BaseModel):
    first_name: str
    last_name: str
    cntry: str
    inst_name: str | None = None
    years: List[int] | None = None

    @validator('years', pre=True, always=True)
    def set_default_years(cls, v):
        return v or [2020, 2021, 2022, 2023]


@app.get("/", tags=["Root"], summary="根端点")
async def read_root():
    return {"message": "Welcome TOP-2 Scientists Analysis API"}


@app.post("/search_author", tags=["Search"], summary="search author")
async def search_author_api(request: SearchRequest):
    year = 2023
    if year not in dfs:
        raise HTTPException(status_code=400, detail="2023 invalid")

    logger.info("[%s] search_author : first_name='%s' last_name='%s' country='%s'",
                datetime.now(), request.first_name, request.last_name, request.country)
    try:
        matches = dfs[year].copy()

        if request.first_name:
            matches = matches[matches['first_name'].str.lower().str.contains(request.first_name.lower(), na=False)]
        if request.last_name:
            matches = matches[matches['last_name'].str.lower().str.contains(request.last_name.lower(), na=False)]
        if request.country:
            cntry_map = {
                "china": "chn", "cn": "chn", "chn": "chn",
                "hong kong": "hkg", "hk": "hkg", "hkg": "hkg",
                "australia": "aus", "aus": "aus", "au": "aus"
            }
            normalized_cntry = cntry_map.get(request.country.lower(), request.country.lower())
            matches = matches[matches['cntry'].str.lower() == normalized_cntry]

        if not request.first_name and not request.last_name:
            return {"type": "not_found"}

        if len(matches) == 0:
            return {"type": "not_found"}

        if request.first_name and request.last_name and request.country and len(matches) == 1:
            author = matches.iloc[0]
            return format_author_response(author)

        options = [
            {
                "authfull": row['authfull'],
                "cntry": row['cntry'],
                "inst_name": row['inst_name'],
                "first_name": row['first_name'],
                "last_name": row['last_name']
            }
            for _, row in matches.iterrows()
        ]
        return {
            "type": "ambiguous",
            "options": options
        }

    except Exception as e:
        logger.error("fail to search: %s", str(e))
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/analyze_author", tags=["Analysis"], summary="Analyze author")
async def analyze_author(
        first_name: str = Query(..., min_length=1),
        last_name: str = Query(..., min_length=1),
        country: str = Query(None)
):

    logger.info("[%s] receive analysis request - %s %s %s", datetime.now(), first_name, last_name, country or '')
    try:
        matches = dfs[2023].copy()
        query = (
                (matches["first_name"].str.lower() == first_name.lower()) &
                (matches["last_name"].str.lower() == last_name.lower())
        )
        if country:
            cntry_map = {"china": "chn", "cn": "chn", "chn": "chn", "hong kong": "hkg", "hk": "hkg", "hkg": "hkg"}
            normalized_cntry = cntry_map.get(country.lower(), country.lower())
            query &= (matches['cntry'].str.lower() == normalized_cntry)

        matched = matches[query]

        if matched.empty and country:
            query = (
                    (matches["first_name"].str.lower() == first_name.lower()) &
                    (matches["last_name"].str.lower() == last_name.lower())
            )
            matched = matches[query]

        if matched.empty:
            raise HTTPException(
                status_code=404,
                detail={
                    "error": "Author not found",
                    "message": f"No match for {first_name} {last_name}",
                    "suggestions": get_suggestions(first_name, last_name)
                }
            )

        author = matched.iloc[0]
        response = format_author_response(author)
        logger.info("result: %s", author['full_name'])
        return response

    except Exception as e:
        logger.error("fail: %s", str(e))
        raise HTTPException(status_code=500, detail={"error": "Analysis failed", "message": str(e)})


def to_native(val):

    if isinstance(val, (np.generic, np.ndarray)):
        return val.item() if isinstance(val, np.generic) else val.tolist()
    if pd.isna(val):
        return 0 if isinstance(val, (float, int)) else "N/A"
    return val


def format_author_response(author):

    metrics = {
        "Papers (1960-2023)": to_native(author.get('np6023', author.get('total_pubs', 0))),
        "Citations (2023)": to_native(author.get('nc2323 (ns)', 0)),
        "H-Index (2023)": to_native(author.get('h23 (ns)', 0)),
        "Composite Score": to_native(author.get('c (ns)', 0)),
        "Self-Citation %": to_native(author.get('self%', 0))
    }

    return {
        "type": "exact",
        "author": {
            "name": str(author['full_name']),
            "first_name": str(author['first_name']),
            "last_name": str(author['last_name']),
            "cntry": str(author['cntry']),
            "institution": str(author['inst_name']),
            "rank": to_native(author.get('rank (ns)', 0)),
            "main_field": str(author.get('sm-field', "Unknown"))
        },
        "metrics": metrics,
        "analysis_data": {
            "np6023": to_native(author.get('np6023', author.get('total_pubs', 0))),
            "nc2323": to_native(author.get('nc2323 (ns)', 0)),
            "h_index": to_native(author.get('h23 (ns)', 0)),
            "composite_score": to_native(author.get('c (ns)', 0))
        }
    }


def get_suggestions(first_name, last_name, limit=3):

    suggestions = dfs[2023][
        (dfs[2023]["first_name"].str.lower().str.startswith(first_name.lower()[0])) &
        (dfs[2023]["last_name"].str.lower() == last_name.lower())
        ].head(limit)
    return [
        {
            "name": f"{row['first_name']} {row['last_name']}",
            "cntry": row['cntry'],
            "institution": row['inst_name'],
            "inst_name": row['inst_name']
        }
        for _, row in suggestions.iterrows()
    ]


def normalize_name(name):

    name = name.replace(",", "").strip().lower()
    return " ".join(name.split())


def load_author_data(first_name, last_name, cntry, inst_name=None):

    logger.info("[%s] search author: first_name=%s, last_name=%s, cntry=%s, inst_name=%s",
                datetime.now(), first_name, last_name, cntry, inst_name)
    input_name_variants = [
        normalize_name(f"{first_name} {last_name}"),
        normalize_name(f"{last_name} {first_name}"),
        normalize_name(f"{last_name}, {first_name}")
    ]
    logger.info(" %s", input_name_variants)

    cntry_map = {
        "china": "chn", "cn": "chn", "chn": "chn",
        "hong kong": "hkg", "hk": "hkg", "hkg": "hkg",
        "australia": "aus", "aus": "aus", "au": "aus"
    }
    normalized_cntry = cntry_map.get(cntry.lower(), cntry.lower())

    result = {}
    for year in [2020, 2021, 2022, 2023]:
        if year not in dfs:
            continue
        df = dfs[year].copy()
        df['authfull_cleaned'] = (
            df['authfull']
            .str.replace(",", "", regex=False)
            .str.replace(r"\s+", " ", regex=True)
            .str.strip()
            .str.lower()
        )
        df['cntry'] = df['cntry'].str.strip().str.lower()
        df['inst_name'] = df['inst_name'].str.strip().str.lower()

        author_rows = df[
            (df['authfull_cleaned'].isin(input_name_variants)) &
            (df['cntry'] == normalized_cntry)
            ]

        if author_rows.empty:
            logger.info("cannot find in", year)
            author_rows = df[
                df['authfull_cleaned'].isin(input_name_variants)
            ]

        if author_rows.empty:
            logger.info("cannot match", year)
            continue

        if inst_name is not None:
            inst_name = inst_name.strip().lower()
            author_rows = author_rows[author_rows['inst_name'] == inst_name]
            if author_rows.empty:
                logger.info("no match", inst_name, year)
                continue

        if len(author_rows) > 1:
            suggestions = [
                {
                    "name": f"{row['first_name']} {row['last_name']}",
                    "cntry": row['cntry'],
                    "institution": row['inst_name'],
                    "inst_name": row['inst_name']
                }
                for _, row in author_rows.iterrows()
            ]
            logger.warning("find multiple matching authors: %s", year, suggestions)
            raise HTTPException(
                status_code=400,
                detail={
                    "message": f"find multiple matching authors {first_name} {last_name}(country: {cntry}, year: {year})",
                    "suggestions": suggestions
                }
            )

        result[year] = author_rows.iloc[0]
        logger.info("authfull='%s', inst_name='%s'", year, result[year]['authfull'],
                    result[year]['inst_name'])

    if not result:
        raise HTTPException(
            status_code=404,
            detail={
                "suggestions": get_suggestions(first_name, last_name)
            }
        )
    return result


@app.post("/api/generate_analysis", tags=["Analysis"], summary="generate analysis")
async def generate_analysis(request: GenerateAnalysisRequest):
    logger.info("[%s] receive generate_analysis request: %s %s %s inst_name=%s years=%s",
                datetime.now(), request.first_name, request.last_name, request.cntry, request.inst_name, request.years)
    try:
        author_data = load_author_data(
            request.first_name, request.last_name, request.cntry, request.inst_name
        )

        analysis_results = {}
        for year in request.years:
            if year not in author_data:
                logger.info("no data, jump ", year)
                analysis_results[year] = {
                    "year": year,
                    "total_publications": 0,
                    "average_publications_per_year": 0,
                    "rank_ns": 0,
                    "rank": 0,
                    "self_citation_rate": 0,
                    "self_citation_level": "Low",
                    "h_index_ns": 0,
                    "cites_ns": 0,
                    "cites": 0,
                    "composite_ns": 0,
                    "citation_ratio_ns": 0,
                    "main_field": "Unknown",
                    "subfield": "Unknown",
                    "npsfl": 0,
                    "cpsf": 0,
                    "nps": 0,
                    "firstyr": "N/A",
                    "lastyr": "N/A",
                    "summary": "No data available for this year."
                }
                continue

            row = author_data[year]
            fields = FIELD_MAPPINGS[year]
            firstyr = int(to_native(row.get("firstyr", 0)))
            lastyr = int(to_native(row.get("lastyr", 0)))
            total_pubs = int(to_native(row.get(fields['total_pubs'], 0)))
            avg_per_year = total_pubs / (lastyr - firstyr + 1) if lastyr > firstyr else 0
            rank_ns = int(to_native(row.get("rank (ns)", 0)))
            rank = int(to_native(row.get("rank", 0)))
            self_rate = float(to_native(row.get("self%", 0)))
            self_rate_level = "Low" if self_rate*100 < 10 else "Moderate" if self_rate*100 < 20 else "High"

            h_index_ns = float(to_native(row.get(fields['h_index_ns'], 0)))
            cites_ns = int(to_native(row.get(fields['cites_ns'], 0)))
            cites = int(to_native(row.get(fields['cites'], 0)))
            citing_ns = int(to_native(row.get("npciting (ns)", 0)))
            composite_ns = float(to_native(row.get("c (ns)", 0)))
            npsfl = int(to_native(row.get(fields['npsfl'], 0)))
            cpsf = int(to_native(row.get(fields['cpsf'], 0)))
            nps = int(to_native(row.get(fields['nps'], 0)))

            ratio_ns = cites_ns / citing_ns if citing_ns > 0 else 0

            summary = (
                f"Author Impact Analysis Report for {year}:\n"
                f"The author has published {total_pubs} papers from {firstyr} to {lastyr}, "
                f"with an average of {avg_per_year:.2f} papers per year.\n"
                f"The author has been cited {cites} times, with an H-index of {h_index_ns:.2f}, "
                f"and citations from {citing_ns} distinct sources.\n"
                f"The self-citation rate is {self_rate*100:.2f}%, which is {self_rate_level.lower()}.\n"
                f"Research is primarily focused on {row.get('sm-subfield-1', 'Unknown')}."
            )

            analysis_results[year] = {
                "year": year,
                "total_publications": total_pubs,
                "average_publications_per_year": round(avg_per_year, 2),
                "rank_ns": rank_ns,
                "rank": rank,
                "self_citation_rate": self_rate,
                "self_citation_level": self_rate_level,
                "h_index_ns": h_index_ns,
                "cites_ns": cites_ns,
                "cites": cites,
                "composite_ns": composite_ns,
                "citation_ratio_ns": ratio_ns,
                "main_field": str(row.get("sm-field", "Unknown")),
                "subfield": str(row.get("sm-subfield-1", "Unknown")),
                "npsfl": npsfl,
                "cpsf": cpsf,
                "nps": nps,
                "firstyr": firstyr,
                "lastyr": lastyr,
                "summary": summary
            }

        if not analysis_results:
            raise HTTPException(
                status_code=404,
                detail={
                    "message": f"cannot find {request.first_name} {request.last_name} ",
                    "suggestions": get_suggestions(request.first_name, request.last_name)
                }
            )

        return {
            "author": {
                "first_name": request.first_name,
                "last_name": request.last_name,
                "cntry": request.cntry,
                "inst_name": request.inst_name or "Unknown",
                #"main_field": analysis_results.get(2023, {}).get("main_field", "Unknown")
            },
            "analysis": analysis_results
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error("fail to analyze: %s", str(e))
        raise HTTPException(status_code=500, detail=str(e))

