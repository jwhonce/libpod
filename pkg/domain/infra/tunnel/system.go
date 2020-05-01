package tunnel

import (
	"context"
	"errors"

	"github.com/spf13/pflag"

	"github.com/containers/libpod/libpod/define"
	"github.com/containers/libpod/pkg/bindings/system"
	"github.com/containers/libpod/pkg/domain/entities"
	"github.com/spf13/cobra"
)

func (ic *ContainerEngine) Info(ctx context.Context) (*define.Info, error) {
	return system.Info(ic.ClientCxt)
}

func (ic *ContainerEngine) VarlinkService(_ context.Context, _ entities.ServiceOptions) error {
	panic(errors.New("varlink service is not supported when tunneling"))
}

func (ic *ContainerEngine) SetupRootless(_ context.Context, cmd *cobra.Command) error {
	panic(errors.New("rootless engine mode is not supported when tunneling"))
}

func (ic *ContainerEngine) SystemRenumber(ctx context.Context, flags *pflag.FlagSet, config *entities.PodmanConfig) error {
	panic(errors.New("system renumber is not supported on remote clients"))
}

func (ic *ContainerEngine) SystemMigrate(ctx context.Context, options entities.SystemMigrateOptions, flags *pflag.FlagSet, config *entities.PodmanConfig) error {
	panic(errors.New("system migrate is not supported on remote clients"))
}

func (ic *ContainerEngine) SystemDf(ctx context.Context, options entities.SystemDfOptions) (*entities.SystemDfReport, error) {
	panic(errors.New("system df is not supported on remote clients"))
}

func (ic *ContainerEngine) SystemReset(ctx context.Context, options entities.SystemResetOptions) error {
	panic(errors.New("system df is not supported on remote clients"))
}
