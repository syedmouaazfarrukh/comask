"""Application configuration using Pydantic Settings."""

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
from typing import Literal


class Settings(BaseSettings):
    """Application settings with environment variable support."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

    # Application
    app_name: str = Field(default="Colorado Energy Compliance Assistant", description="Application name")
    app_env: str = Field(default="development", description="Environment")
    debug: bool = Field(default=False, description="Debug mode")
    secret_key: str = Field(default="change-me-in-production", description="Secret key for JWT")

    # Database (PostgreSQL with pgvector)
    database_url: str = Field(
        default="postgresql+asyncpg://comask:comask_dev_password@localhost:5432/comask",
        description="PostgreSQL connection URL"
    )
    database_name: str = Field(default="comask", description="Database name")

    # Vector Database Settings
    vector_dimension: int = Field(
        default=1024,
        description="Vector embedding dimension (Voyage AI default)"
    )

    # LLM Provider
    llm_provider: Literal["claude", "azure_openai", "groq"] = Field(
        default="claude",
        description="LLM provider"
    )

    # Claude API (Primary)
    claude_api_key: str = Field(
        default="",
        description="Anthropic Claude API key"
    )
    claude_model_fast: str = Field(
        default="claude-sonnet-4-20250514",
        description="Claude model for fast responses (Sonnet)"
    )
    claude_model_complex: str = Field(
        default="claude-opus-4-20250514",
        description="Claude model for complex queries (Opus)"
    )
    claude_max_tokens: int = Field(
        default=4096,
        description="Maximum tokens for Claude responses"
    )

    # Voyage AI Embeddings
    voyage_api_key: str = Field(
        default="",
        description="Voyage AI API key for embeddings"
    )
    voyage_model: str = Field(
        default="voyage-3",
        description="Voyage AI model (voyage-3 is the latest general model)"
    )
    voyage_batch_size: int = Field(
        default=128,
        description="Batch size for Voyage AI embedding requests"
    )

    # Azure OpenAI (Legacy/Fallback)
    azure_openai_api_key: str = Field(
        default="",
        description="Azure OpenAI API key"
    )
    azure_openai_endpoint: str = Field(
        default="",
        description="Azure OpenAI endpoint"
    )
    azure_openai_api_version: str = Field(
        default="2024-02-15-preview",
        description="Azure OpenAI API version"
    )
    azure_openai_deployment_name: str = Field(
        default="gpt-4-turbo",
        description="Azure OpenAI deployment name"
    )
    azure_openai_embedding_deployment: str = Field(
        default="",
        description="Azure OpenAI embedding deployment name"
    )
    embedding_model: str = Field(
        default="text-embedding-3-large",
        description="Embedding model name (for Azure OpenAI)"
    )
    embedding_dimension: int = Field(
        default=3072,
        description="Embedding dimension (3072 for text-embedding-3-large)"
    )

    # Groq (Alternative)
    groq_api_key: str = Field(
        default="",
        description="Groq API key"
    )
    groq_model: str = Field(
        default="llama-3-70b-8192",
        description="Groq model name"
    )

    # Authentication
    jwt_algorithm: str = Field(
        default="HS256",
        description="JWT signing algorithm"
    )
    access_token_expire_minutes: int = Field(
        default=1440,  # 24 hours
        description="Access token expiration in minutes"
    )
    refresh_token_expire_days: int = Field(
        default=7,
        description="Refresh token expiration in days"
    )
    password_min_length: int = Field(
        default=8,
        description="Minimum password length"
    )

    # Scraping
    scraper_user_agent: str = Field(
        default="Mozilla/5.0 (Colorado Energy Compliance Assistant)",
        description="User agent for scrapers"
    )
    scraper_delay_seconds: float = Field(
        default=2.0,
        description="Delay between scraping requests"
    )
    scraper_max_retries: int = Field(
        default=3,
        description="Maximum retry attempts"
    )

    # Federal Sources
    ecfr_api_base_url: str = Field(
        default="https://www.ecfr.gov/api/versioner/v1",
        description="eCFR API base URL"
    )
    ferc_base_url: str = Field(
        default="https://elibrary.ferc.gov",
        description="FERC eLibrary base URL"
    )
    federal_register_api_url: str = Field(
        default="https://www.federalregister.gov/api/v1",
        description="Federal Register API URL"
    )

    # Colorado Sources
    cpuc_base_url: str = Field(
        default="https://puc.colorado.gov",
        description="Colorado PUC base URL"
    )
    cpuc_efilings_url: str = Field(
        default="https://www.dora.state.co.us/pls/efi/EFI_Search_UI.search",
        description="Colorado PUC E-Filings URL"
    )
    crs_base_url: str = Field(
        default="https://leg.colorado.gov/colorado-revised-statutes",
        description="Colorado Revised Statutes base URL"
    )
    ccr_base_url: str = Field(
        default="https://www.sos.state.co.us/CCR",
        description="Colorado Code of Regulations base URL"
    )
    ceo_base_url: str = Field(
        default="https://energyoffice.colorado.gov",
        description="Colorado Energy Office base URL"
    )

    # Regional Sources
    nerc_standards_url: str = Field(
        default="https://www.nerc.com/pa/Stand/Pages/ReliabilityStandards.aspx",
        description="NERC Reliability Standards URL"
    )
    wecc_standards_url: str = Field(
        default="https://www.wecc.org/Standards",
        description="WECC Regional Standards URL"
    )
    spp_base_url: str = Field(
        default="https://www.spp.org",
        description="Southwest Power Pool base URL"
    )

    # Redis
    redis_url: str = Field(
        default="redis://localhost:6379/0",
        description="Redis connection URL"
    )

    # Storage
    storage_type: Literal["local", "s3"] = Field(
        default="local",
        description="Storage type"
    )
    storage_path: str = Field(
        default="./storage",
        description="Local storage path"
    )

    # Logging
    log_level: str = Field(
        default="INFO",
        description="Logging level"
    )


# Global settings instance
settings = Settings()
