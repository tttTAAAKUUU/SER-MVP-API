"""Initial migration: Add bidding, pricing ranges, and rating system

Revision ID: 001_add_bidding_system
Revises: 
Create Date: 2026-09-12 14:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "001_add_bidding_system"
down_revision: Union[str, None] = None
branch_labels: Union[Sequence[str], None] = None
depends_on: Union[Sequence[str], None] = None


def upgrade() -> None:
    """Create new tables and add columns for bidding, status tracking, and rating."""
    
    # Create provider_bids table
    op.create_table(
        'provider_bids',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('booking_id', sa.Integer(), nullable=False),
        sa.Column('provider_id', sa.Integer(), nullable=False),
        sa.Column('bid_price', sa.String(), nullable=False),
        sa.Column('bid_message', sa.Text(), nullable=True),
        sa.Column('status', sa.String(20), nullable=False, server_default='PENDING'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.ForeignKeyConstraint(['booking_id'], ['bookings.id'], ),
        sa.ForeignKeyConstraint(['provider_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.Index('ix_provider_bids_booking_id', 'booking_id'),
        sa.Index('ix_provider_bids_provider_id', 'provider_id'),
        sa.Index('ix_provider_bids_status', 'status'),
    )
    
    # Create service_pricing_ranges table
    op.create_table(
        'service_pricing_ranges',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('service_id', sa.Integer(), nullable=False),
        sa.Column('min_price', sa.String(), nullable=False),
        sa.Column('max_price', sa.String(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('category', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.ForeignKeyConstraint(['service_id'], ['services.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.Index('ix_service_pricing_ranges_service_id', 'service_id'),
    )
    
    # Add columns to bookings table for bidding flow
    op.add_column('bookings', sa.Column('bid_status', sa.String(20), nullable=True, server_default='OPEN_FOR_BIDS'))
    op.add_column('bookings', sa.Column('bid_expires_at', sa.DateTime(), nullable=True))
    op.add_column('bookings', sa.Column('final_price', sa.String(), nullable=True))
    
    # Create index on bid_status for filtering
    op.create_index('ix_bookings_bid_status', 'bookings', ['bid_status'])


def downgrade() -> None:
    """Revert changes: drop tables and columns."""
    
    # Drop indexes
    op.drop_index('ix_bookings_bid_status', table_name='bookings')
    
    # Drop columns from bookings
    op.drop_column('bookings', 'final_price')
    op.drop_column('bookings', 'bid_expires_at')
    op.drop_column('bookings', 'bid_status')
    
    # Drop service_pricing_ranges table
    op.drop_index('ix_service_pricing_ranges_service_id', table_name='service_pricing_ranges')
    op.drop_table('service_pricing_ranges')
    
    # Drop provider_bids table
    op.drop_index('ix_provider_bids_status', table_name='provider_bids')
    op.drop_index('ix_provider_bids_provider_id', table_name='provider_bids')
    op.drop_index('ix_provider_bids_booking_id', table_name='provider_bids')
    op.drop_table('provider_bids')
