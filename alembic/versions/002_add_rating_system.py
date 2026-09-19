"""Add rating system columns to provider profiles

Revision ID: 002_add_rating_system
Revises: 001_add_bidding_system
Create Date: 2026-09-12 14:05:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "002_add_rating_system"
down_revision: Union[str, None] = "001_add_bidding_system"
branch_labels: Union[Sequence[str], None] = None
depends_on: Union[Sequence[str], None] = None


def upgrade() -> None:
    """Add rating columns to provider_profiles and create indexes."""
    
    # Add columns to provider_profiles table for rating system
    op.add_column('provider_profiles', sa.Column('average_rating', sa.String(), nullable=True, server_default='0.0'))
    op.add_column('provider_profiles', sa.Column('total_ratings', sa.Integer(), nullable=True, server_default='0'))
    
    # Create index on average_rating for sorting
    op.create_index('ix_provider_profiles_average_rating', 'provider_profiles', ['average_rating'])


def downgrade() -> None:
    """Revert changes: remove rating columns from provider_profiles."""
    
    # Drop index
    op.drop_index('ix_provider_profiles_average_rating', table_name='provider_profiles')
    
    # Drop columns from provider_profiles
    op.drop_column('provider_profiles', 'total_ratings')
    op.drop_column('provider_profiles', 'average_rating')
