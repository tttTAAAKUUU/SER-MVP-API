"""Add service_area field to provider profiles

Revision ID: 003_add_service_area
Revises: 002_add_rating_system
Create Date: 2026-09-12 14:10:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "003_add_service_area"
down_revision: Union[str, None] = "002_add_rating_system"
branch_labels: Union[Sequence[str], None] = None
depends_on: Union[Sequence[str], None] = None


def upgrade() -> None:
    """Add service_area column to provider_profiles table."""
    
    # Add service_area column for location display (e.g., "Bryanston, Sandton")
    op.add_column('provider_profiles', sa.Column('service_area', sa.String(), nullable=True))
    
    # Create index on service_area for geographic filtering
    op.create_index('ix_provider_profiles_service_area', 'provider_profiles', ['service_area'])


def downgrade() -> None:
    """Revert changes: remove service_area column from provider_profiles."""
    
    # Drop index
    op.drop_index('ix_provider_profiles_service_area', table_name='provider_profiles')
    
    # Drop column from provider_profiles
    op.drop_column('provider_profiles', 'service_area')
