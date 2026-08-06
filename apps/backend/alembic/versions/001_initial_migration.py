"""initial_migration

Revision ID: 001
Revises: 
Create Date: 2026-01-01 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create users table
    op.create_table(
        'users',
        sa.Column('id', sa.String(36), nullable=False),
        sa.Column('email', sa.String(255), nullable=False),
        sa.Column('username', sa.String(50), nullable=False),
        sa.Column('full_name', sa.String(100), nullable=True),
        sa.Column('hashed_password', sa.String(255), nullable=False),
        sa.Column('role', sa.String(20), nullable=True, default='user'),
        sa.Column('is_active', sa.Boolean(), nullable=True, default=True),
        sa.Column('is_verified', sa.Boolean(), nullable=True, default=False),
        sa.Column('paritok_api_key', sa.String(255), nullable=True),
        sa.Column('total_tokens_saved', sa.Integer(), nullable=True, default=0),
        sa.Column('total_reviews_count', sa.Integer(), nullable=True, default=0),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('last_login', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email'),
        sa.UniqueConstraint('username')
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)
    op.create_index(op.f('ix_users_username'), 'users', ['username'], unique=True)

    # Create repositories table
    op.create_table(
        'repositories',
        sa.Column('id', sa.String(36), nullable=False),
        sa.Column('user_id', sa.String(36), nullable=False),
        sa.Column('url', sa.String(500), nullable=False),
        sa.Column('name', sa.String(200), nullable=False),
        sa.Column('full_name', sa.String(300), nullable=False),
        sa.Column('default_branch', sa.String(100), nullable=True),
        sa.Column('is_private', sa.Boolean(), nullable=True, default=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_repositories_id'), 'repositories', ['id'], unique=False)
    op.create_index(op.f('ix_repositories_user_id'), 'repositories', ['user_id'], unique=False)

    # Create reviews table
    op.create_table(
        'reviews',
        sa.Column('id', sa.String(36), nullable=False),
        sa.Column('user_id', sa.String(36), nullable=False),
        sa.Column('repository_url', sa.String(500), nullable=False),
        sa.Column('repository_name', sa.String(200), nullable=False),
        sa.Column('pr_number', sa.Integer(), nullable=False),
        sa.Column('pr_title', sa.String(500), nullable=True),
        sa.Column('pr_description', sa.Text(), nullable=True),
        sa.Column('status', sa.String(20), nullable=True, default='pending'),
        sa.Column('diff_content', sa.Text(), nullable=True),
        sa.Column('affected_files', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('original_tokens', sa.Integer(), nullable=True),
        sa.Column('optimized_tokens', sa.Integer(), nullable=True),
        sa.Column('tokens_saved_percentage', sa.Float(), nullable=True),
        sa.Column('optimization_time_ms', sa.Integer(), nullable=True),
        sa.Column('review_output', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('summary', sa.Text(), nullable=True),
        sa.Column('issues_found', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('model_used', sa.String(100), nullable=True),
        sa.Column('temperature', sa.Float(), nullable=True, default=0.7),
        sa.Column('max_tokens', sa.Integer(), nullable=True, default=4000),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_reviews_id'), 'reviews', ['id'], unique=False)
    op.create_index(op.f('ix_reviews_user_id'), 'reviews', ['user_id'], unique=False)
    op.create_index(op.f('ix_reviews_status'), 'reviews', ['status'], unique=False)
    op.create_index(op.f('ix_reviews_pr_number'), 'reviews', ['pr_number'], unique=False)

    # Create token_usage table
    op.create_table(
        'token_usage',
        sa.Column('id', sa.String(36), nullable=False),
        sa.Column('user_id', sa.String(36), nullable=False),
        sa.Column('review_id', sa.String(36), nullable=False),
        sa.Column('original_tokens', sa.Integer(), nullable=False),
        sa.Column('optimized_tokens', sa.Integer(), nullable=False),
        sa.Column('tokens_saved', sa.Integer(), nullable=False),
        sa.Column('savings_percentage', sa.Float(), nullable=False),
        sa.Column('model_used', sa.String(100), nullable=True),
        sa.Column('cost_saved', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['review_id'], ['reviews.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('review_id')
    )
    op.create_index(op.f('ix_token_usage_id'), 'token_usage', ['id'], unique=False)
    op.create_index(op.f('ix_token_usage_user_id'), 'token_usage', ['user_id'], unique=False)

    # Create analytics table
    op.create_table(
        'analytics',
        sa.Column('id', sa.String(36), nullable=False),
        sa.Column('user_id', sa.String(36), nullable=False),
        sa.Column('period', sa.String(20), nullable=False),
        sa.Column('total_reviews', sa.Integer(), nullable=False),
        sa.Column('total_tokens_saved', sa.Integer(), nullable=False),
        sa.Column('total_original_tokens', sa.Integer(), nullable=False),
        sa.Column('total_optimized_tokens', sa.Integer(), nullable=False),
        sa.Column('average_savings_percentage', sa.Float(), nullable=False),
        sa.Column('total_cost_saved', sa.Float(), nullable=True),
        sa.Column('date_range', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('generated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_analytics_id'), 'analytics', ['id'], unique=False)
    op.create_index(op.f('ix_analytics_user_id'), 'analytics', ['user_id'], unique=False)
    op.create_index(op.f('ix_analytics_period'), 'analytics', ['period'], unique=False)
    op.create_index(op.f('ix_analytics_generated_at'), 'analytics', ['generated_at'], unique=False)


def downgrade() -> None:
    op.drop_index('ix_analytics_generated_at', table_name='analytics')
    op.drop_index('ix_analytics_period', table_name='analytics')
    op.drop_table('analytics')
    op.drop_table('token_usage')
    op.drop_index(op.f('ix_reviews_pr_number'), table_name='reviews')
    op.drop_index(op.f('ix_reviews_status'), table_name='reviews')
    op.drop_table('reviews')
    op.drop_table('repositories')
    op.drop_table('users')
