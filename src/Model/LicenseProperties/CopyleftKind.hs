{-# LANGUAGE ExistentialQuantification #-}
{-# LANGUAGE TypeFamilies #-}
{-# LANGUAGE GADTs #-}
{-# LANGUAGE OverloadedStrings #-}
{-# LANGUAGE DeriveGeneric #-}
module Model.LicenseProperties.CopyleftKind
    where

import qualified Prelude as P
import           MyPrelude

import qualified Data.Map as M

{-
    CopyleftKind
     | \
     |  - Copyleft
     |     | \
     |     |  - StrongCopyleft
     |     |     \
     |     |      - SaaSCopyleft
     |     \
     |       - WeakCopyleft
     \
      - NoCopyleft
 -}
data CopyleftKind
  = StrongCopyleft
  | WeakCopyleft
  | SaaSCopyleft
  | Copyleft
  | NoCopyleft
  deriving (Eq, Show, Generic)
instance ToJSON CopyleftKind
instance Ord CopyleftKind where
  compare k1 k2 = let
      kOrder = M.fromList [ (StrongCopyleft, 5 :: Int)
                          , (WeakCopyleft, 4)
                          , (SaaSCopyleft, 3)
                          , (Copyleft, 2)
                          , (NoCopyleft, 1) ]
    in if k1 == k2
       then EQ
       else compare (kOrder M.! k1)  (kOrder M.! k2)
pessimisticMergeCopyleft :: CopyleftKind -> CopyleftKind -> CopyleftKind
-- pessimisticMergeCopyleft = max
pessimisticMergeCopyleft SaaSCopyleft _        = SaaSCopyleft
pessimisticMergeCopyleft _ SaaSCopyleft        = SaaSCopyleft
pessimisticMergeCopyleft StrongCopyleft _      = StrongCopyleft
pessimisticMergeCopyleft _ StrongCopyleft      = StrongCopyleft
pessimisticMergeCopyleft WeakCopyleft _        = WeakCopyleft
pessimisticMergeCopyleft _ WeakCopyleft        = WeakCopyleft
pessimisticMergeCopyleft Copyleft _            = Copyleft
pessimisticMergeCopyleft _ Copyleft            = Copyleft
pessimisticMergeCopyleft NoCopyleft NoCopyleft = NoCopyleft


